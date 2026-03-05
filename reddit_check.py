"""
reddit_check.py — validate trend signals against Reddit discussion

Searches targeted subreddits with pain-framed queries to check whether
real people are actively frustrated about a topic. Routes each cluster
to relevant communities based on category/keyword matching.

Rate limit: Reddit allows ~10 requests/min from unauthenticated clients.
We check top clusters (up to 3 subreddits × 2 queries each, 3 clusters max).
"""

import json
import time
import urllib.request
import urllib.error
from collections import Counter

from cluster import _stem

# User-Agent required by Reddit
_HEADERS = {
    "User-Agent": "TrendDetector/1.0 (private pipeline; contact: modryn-studio)",
}

# Minimum seconds between Reddit requests
_REQUEST_DELAY = 2.0

# --- Subreddit routing ---
# Map topic domains to subreddits where real users express pain.
# General-purpose subs are appended when no specific match is found.
SUBREDDIT_MAP = {
    "social": ["socialskills", "makingfriends", "lonely", "introvert", "Advice"],
    "community": ["socialskills", "makingfriends", "lonely", "introvert", "community"],
    "friend": ["socialskills", "makingfriends", "lonely", "Advice"],
    "travel": ["solotravel", "travel", "digitalnomad", "Shoestring", "TravelHacks"],
    "flight": ["travel", "flights", "TravelHacks", "solotravel"],
    "hotel": ["travel", "Hotels", "TravelHacks"],
    "finance": ["personalfinance", "investing", "FinancialPlanning", "povertyfinance"],
    "stock": ["stocks", "investing", "wallstreetbets", "StockMarket"],
    "crypto": ["CryptoCurrency", "Bitcoin", "CryptoMarkets"],
    "tech": ["webdev", "SaaS", "startups", "sideproject", "EntrepreneurRideAlong"],
    "app": ["webdev", "SaaS", "startups", "androidapps", "iosapps"],
    "tool": ["webdev", "SaaS", "startups", "InternetIsBeautiful", "productivity"],
    "health": ["HealthIT", "selfimprovement", "loseit", "Fitness"],
    "fitness": ["Fitness", "bodyweightfitness", "GYM", "loseit"],
    "food": ["Cooking", "MealPrepSunday", "EatCheapAndHealthy"],
    "career": ["careerguidance", "cscareerquestions", "jobs", "antiwork"],
    "education": ["learnprogramming", "college", "GradSchool", "studytips"],
    "housing": ["realestate", "FirstTimeHomeBuyer", "personalfinance"],
}

# Fallback subreddits when no domain match is found
_GENERAL_SUBS = ["NoStupidQuestions", "Advice", "findareddit", "internetparents"]

# Pain-framing query templates — search the frustration, not the keyword.
# Multiple angles: direct frustration, emotional barrier, solution-seeking.
_PAIN_TEMPLATES = [
    "{kw} frustrated OR struggling OR overwhelmed OR \"wish there was\"",
    "afraid OR anxious OR nervous {kw}",
    "{kw} \"looking for\" OR \"any good\" OR \"is there a\" OR recommendation",
]

def _generate_pain_queries(cluster_name: str, top_keyword: str,
                           members: list[dict]) -> list[str]:
    """Use GPT-5 mini to generate underlying Reddit search queries.

    Instead of searching the coined trend term (e.g. "boy kibble"),
    we surface the underlying human problem using language real people
    used before the trend had a name (e.g. "easy high protein meals
    single guy"). Falls back to _PAIN_TEMPLATES if the call fails.

    Uses the Responses API (correct API for reasoning models) with
    reasoning effort=low — fast and cheap for this simple reframing task.
    """
    try:
        from openai import OpenAI
        kws = [m["keyword"] for m in members[:6]]
        prompt = (
            f'Trending cluster: "{cluster_name}"\n'
            f'Top keyword: "{top_keyword}"\n'
            f'Related: {", ".join(kws)}\n\n'
            f'Generate 3 short Reddit search queries a real person would '
            f'type when frustrated by this problem, before they knew this '
            f'trend had a name. Everyday language only, no trend jargon. '
            f'Each query 3-7 words.\n\n'
            f'Return ONLY valid JSON: {{"queries": ["q1", "q2", "q3"]}}'
        )
        resp = OpenAI().responses.create(
            model="gpt-5-mini",
            reasoning={"effort": "low"},
            input=[{"role": "user", "content": prompt}],
            text={"format": {"type": "json_object"}},
            max_output_tokens=1000,
        )
        data = json.loads(resp.output_text)
        queries = data.get("queries", [])
        if isinstance(queries, list) and len(queries) >= 2:
            return [str(q) for q in queries[:3]]
    except Exception:
        pass
    # Fallback: pain templates with the best search keyword
    return [t.format(kw=top_keyword) for t in _PAIN_TEMPLATES]


# Pain language patterns — checked against post titles AND selftext
_PAIN_PHRASES = [
    "wish", "need", "looking for", "frustrated", "struggle",
    "lonely", "hard to find", "difficult", "impossible", "can't find",
    "where can i", "does anyone know", "alternative to",
    "nothing works", "sick of", "tired of", "help me find",
    "recommendation", "suggest", "any good", "is there a",
    "how do i", "where do i", "why is it so hard",
]


def _route_subreddits(cluster: dict) -> list[str]:
    """Pick 3-5 relevant subreddits for a cluster based on keywords and category."""
    texts = [cluster["cluster_name"].lower()]
    for m in cluster["members"][:5]:
        texts.append(m["keyword"].lower())
    if cluster.get("category"):
        texts.append(cluster["category"].lower())
    all_text = " ".join(texts)

    matched_subs: list[str] = []
    seen: set[str] = set()
    for domain, subs in SUBREDDIT_MAP.items():
        if domain in all_text:
            for s in subs:
                if s not in seen:
                    matched_subs.append(s)
                    seen.add(s)

    if not matched_subs:
        matched_subs = list(_GENERAL_SUBS)

    return matched_subs[:5]


def _search_subreddit(subreddit: str, query: str,
                      limit: int = 15,
                      time_filter: str = "month") -> list[dict]:
    """Search a specific subreddit. Returns list of post dicts."""
    encoded_q = urllib.request.quote(query, safe='')
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={encoded_q}&restrict_sr=1&sort=relevance"
        f"&t={time_filter}&limit={limit}"
    )
    req = urllib.request.Request(url, headers=_HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return []

    posts_raw = data.get("data", {}).get("children", [])
    results = []
    for p in posts_raw:
        pd = p.get("data", {})
        results.append({
            "title":        pd.get("title", ""),
            "selftext":     pd.get("selftext", "")[:500],
            "subreddit":    pd.get("subreddit", subreddit),
            "score":        pd.get("score", 0),
            "url":          f"https://reddit.com{pd.get('permalink', '')}",
            "num_comments": pd.get("num_comments", 0),
            "created_utc":  pd.get("created_utc", 0),
        })
    return results


def check_reddit(keyword: str, cluster: dict | None = None,
                 limit: int = 25,
                 time_filter: str = "month") -> dict:
    """
    Search targeted subreddits with pain-framed queries for a keyword.

    If a cluster is provided, routes to relevant subreddits.
    Otherwise falls back to general subreddits.
    """
    if cluster:
        target_subs = _route_subreddits(cluster)
        # Generate underlying problem queries via LLM — searches the human
        # pain that predates the trend name rather than the coined term itself.
        queries = _generate_pain_queries(
            cluster["cluster_name"], keyword, cluster.get("members", [])
        )
    else:
        target_subs = list(_GENERAL_SUBS)
        queries = [t.format(kw=keyword) for t in _PAIN_TEMPLATES]

    all_posts: list[dict] = []
    seen_urls: set[str] = set()
    sub_counter: Counter = Counter()

    for sub in target_subs:
        for query in queries:
            time.sleep(_REQUEST_DELAY)
            per_query_limit = max(5, limit // (len(queries) * len(target_subs)))
            results = _search_subreddit(sub, query, limit=per_query_limit,
                                        time_filter=time_filter)
            for p in results:
                if p["url"] not in seen_urls:
                    seen_urls.add(p["url"])
                    all_posts.append(p)
                    sub_counter[p["subreddit"]] += 1

    # Sort by engagement
    all_posts.sort(key=lambda p: p["score"] + p["num_comments"], reverse=True)
    top = all_posts[:10]

    # Pain signal — check titles AND selftext
    pain_signal = False
    for p in all_posts:
        searchable = (p["title"] + " " + p.get("selftext", "")).lower()
        if any(pw in searchable for pw in _PAIN_PHRASES):
            pain_signal = True
            break

    # Reliability: at least 2 of top 10 posts must contain a keyword stem
    kw_stems = {
        _stem(w) for w in keyword.lower().split()
        if w not in {"a", "an", "the", "to", "for", "of", "in", "how",
                     "is", "are", "i", "my", "do", "can", "near", "me"}
        and len(w) > 2
    }

    on_topic = 0
    for p in all_posts[:10]:
        searchable = (p["title"] + " " + p.get("selftext", "")).lower()
        if any(stem in searchable for stem in kw_stems):
            on_topic += 1

    pain_reliable = pain_signal and on_topic >= 2

    # Keep selftext (truncated to 300 chars) so briefing can show pain excerpts
    brief_posts = []
    for p in top:
        post = dict(p)
        body = post.get("selftext", "")
        post["selftext"] = body[:300].rstrip() if body else ""
        brief_posts.append(post)

    return {
        "keyword":         keyword,
        "pain_queries":    queries,
        "total_posts":     len(all_posts),
        "subreddit_hits":  dict(sub_counter.most_common(10)),
        "top_posts":       brief_posts,
        "pain_signal":     pain_signal,
        "pain_reliable":   pain_reliable,
        "targeted_subs":   target_subs,
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
    For the top N clusters, run targeted Reddit validation.
    Mutates clusters in-place, adding 'reddit' field.
    """
    for i, cluster in enumerate(clusters[:max_checks]):
        kw = _best_search_keyword(cluster)
        print(f"[reddit] Checking: {kw}  (cluster: {cluster['cluster_name']})")
        result = check_reddit(kw, cluster=cluster)
        cluster["reddit"] = result

        subs = list(result["subreddit_hits"].keys())[:3]
        sub_str = ", ".join(f"r/{s}" for s in subs) if subs else "none"
        reliable_tag = " (reliable)" if result["pain_reliable"] else ""
        print(f"[reddit]   {result['total_posts']} posts  "
              f"subs=[{sub_str}]  "
              f"pain_signal={result['pain_signal']}{reliable_tag}")

    return clusters


# --- Standalone test ---
if __name__ == "__main__":
    import sys
    keyword = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "friend app"
    print(f"Searching Reddit for '{keyword}'...\n")
    result = check_reddit(keyword)
    print(f"Total posts: {result['total_posts']}")
    print(f"Targeted subs: {result['targeted_subs']}")
    print(f"Subreddits: {result['subreddit_hits']}")
    print(f"Pain signal: {result['pain_signal']} (reliable: {result['pain_reliable']})")
    print(f"\nTop posts:")
    for p in result["top_posts"][:5]:
        print(f"  [r/{p['subreddit']}] {p['title']}")
        print(f"    score={p['score']}  comments={p['num_comments']}")
        print(f"    {p['url']}")
