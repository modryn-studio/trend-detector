"""
reddit_check.py — validate trend signals against Reddit discussion

Hits Reddit's public JSON search (no API key, no auth) to check whether
real people are actively discussing a topic. Searches ALL of Reddit —
the results tell us which communities care, rather than us guessing.

Rate limit: Reddit allows ~10 requests/min from unauthenticated clients.
We only check top clusters (1 query per cluster, 3 clusters max).
"""

import json
import time
import urllib.request
import urllib.error
from collections import Counter

# User-Agent required by Reddit
_HEADERS = {
    "User-Agent": "TrendDetector/1.0 (private pipeline; contact: modryn-studio)",
}

# Minimum seconds between Reddit requests
_REQUEST_DELAY = 2.0


def check_reddit(keyword: str,
                 limit: int = 25,
                 time_filter: str = "month") -> dict:
    """
    Search ALL of Reddit for a keyword.

    Returns:
    {
        "keyword": "friend app",
        "total_posts": 12,
        "subreddit_hits": {"socialskills": 5, "lonely": 4, "SaaS": 3},
        "top_posts": [...],
        "pain_signal": True/False
    }
    """
    url = (
        f"https://www.reddit.com/search.json"
        f"?q={urllib.request.quote(keyword, safe='')}"
        f"&sort=relevance&t={time_filter}&limit={limit}"
    )
    req = urllib.request.Request(url, headers=_HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        print(f"[reddit] Search failed for '{keyword}': {e}")
        return {
            "keyword": keyword, "total_posts": 0,
            "subreddit_hits": {}, "top_posts": [], "pain_signal": False,
        }

    posts_raw = data.get("data", {}).get("children", [])
    all_posts: list[dict] = []
    sub_counter: Counter = Counter()

    for p in posts_raw:
        pd = p.get("data", {})
        sub = pd.get("subreddit", "unknown")
        sub_counter[sub] += 1
        all_posts.append({
            "title":        pd.get("title", ""),
            "subreddit":    sub,
            "score":        pd.get("score", 0),
            "url":          f"https://reddit.com{pd.get('permalink', '')}",
            "num_comments": pd.get("num_comments", 0),
            "created_utc":  pd.get("created_utc", 0),
        })

    # Sort by engagement (score + comments)
    all_posts.sort(key=lambda p: p["score"] + p["num_comments"], reverse=True)
    top = all_posts[:10]

    # Pain signal — frustration language in titles
    pain_words = [
        "wish", "need", "looking for", "frustrated", "struggle",
        "lonely", "hard to", "difficult", "impossible", "can't find",
        "where can i", "does anyone know", "alternative to",
        "nothing works", "sick of", "tired of", "help me",
        "recommendation", "suggest", "any good",
    ]
    pain_signal = any(
        any(pw in p["title"].lower() for pw in pain_words)
        for p in all_posts
    )

    # Reliability check — are the results actually about this keyword?
    # At least 1 of the top 5 posts should mention a meaningful keyword word.
    kw_words = {
        w for w in keyword.lower().split()
        if w not in {"a", "an", "the", "to", "for", "of", "in", "how",
                     "is", "are", "i", "my", "do", "can", "near", "me"}
        and len(w) > 2
    }
    on_topic = sum(
        1 for p in all_posts[:5]
        if any(w in p["title"].lower() for w in kw_words)
    )
    # Signal is reliable if at least 1 post is visibly on-topic
    pain_reliable = pain_signal and on_topic >= 1

    return {
        "keyword":        keyword,
        "total_posts":    len(all_posts),
        "subreddit_hits": dict(sub_counter.most_common(10)),
        "top_posts":      top,
        "pain_signal":    pain_signal,
        "pain_reliable":  pain_reliable,
    }


def _best_search_keyword(cluster: dict) -> str:
    """Pick the most searchable keyword for this cluster.

    Reddit's search works best with 2-5 word phrases. Prefer breakout
    members that aren't truncated. Fall back to the cluster name if it's
    short and descriptive (email-sourced clusters = natural English names).
    """
    def _word_count_score(kw: str) -> int:
        """Prefer keywords closest to 3 words."""
        return abs(len(kw.split()) - 3)

    def _is_clean(kw: str) -> bool:
        """Reject truncated or malformed keywords."""
        return "..." not in kw and "\u2026" not in kw and len(kw.split()) >= 2

    # Breakout members with clean 2-5 word phrases
    candidates = [
        m["keyword"] for m in cluster["members"]
        if m.get("_raw", {}).get("google_growth_pct", 0) >= 5000
        and _is_clean(m["keyword"])
        and 2 <= len(m["keyword"].split()) <= 5
    ]
    if candidates:
        return min(candidates, key=_word_count_score)

    # Cluster name itself works well for email-sourced clusters ("Making Friends")
    name = cluster["cluster_name"]
    if " / " not in name and 1 <= len(name.split()) <= 4:
        return name

    # Last resort: top_keyword trimmed to 5 words
    top = cluster["top_keyword"]
    return " ".join(top.split()[:5])


def validate_clusters(clusters: list[dict],
                      max_checks: int = 3) -> list[dict]:
    """
    For the top N clusters, run Reddit validation using the best available
    search keyword (not necessarily top_keyword — see _best_search_keyword).
    Mutates clusters in-place, adding 'reddit' field.
    """
    for i, cluster in enumerate(clusters[:max_checks]):
        if i > 0:
            time.sleep(_REQUEST_DELAY)
        kw = _best_search_keyword(cluster)
        print(f"[reddit] Checking: {kw}  (cluster: {cluster['cluster_name']})")
        result = check_reddit(kw)
        cluster["reddit"] = result

        subs = list(result["subreddit_hits"].keys())[:3]
        sub_str = ", ".join(f"r/{s}" for s in subs) if subs else "none"
        print(f"[reddit]   {result['total_posts']} posts  "
              f"subs=[{sub_str}]  "
              f"pain_signal={result['pain_signal']}")

    return clusters


# --- Standalone test ---
if __name__ == "__main__":
    import sys
    keyword = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "friend app"
    print(f"Searching Reddit for '{keyword}'...\n")
    result = check_reddit(keyword)
    print(f"Total posts: {result['total_posts']}")
    print(f"Subreddits: {result['subreddit_hits']}")
    print(f"Pain signal: {result['pain_signal']}")
    print(f"\nTop posts:")
    for p in result["top_posts"][:5]:
        print(f"  [r/{p['subreddit']}] {p['title']}")
        print(f"    score={p['score']}  comments={p['num_comments']}")
        print(f"    {p['url']}")
