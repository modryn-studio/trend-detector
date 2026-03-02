"""
reddit_check.py — validate trend signals against Reddit discussion

Hits Reddit's public JSON search (no API key, no auth) to check whether
real people are actively discussing a topic. High-signal subreddits for
building opportunities.

Rate limit: Reddit allows ~10 requests/min from unauthenticated clients.
We batch carefully and only check top clusters (3-5 queries per run).
"""

import json
import time
import urllib.request
import urllib.error

# Subreddits most likely to contain "I wish a tool existed" language
VALIDATION_SUBS = [
    "MakeNewFriendsHere",
    "socialskills",
    "lonely",
    "SaaS",
    "entrepreneur",
    "webdev",
    "startups",
    "Needafriend",
]

# User-Agent required by Reddit
_HEADERS = {
    "User-Agent": "TrendDetector/1.0 (private pipeline; contact: modryn-studio)",
}

# Minimum seconds between Reddit requests
_REQUEST_DELAY = 2.0


def check_reddit(keyword: str,
                 subreddits: list[str] | None = None,
                 limit: int = 5,
                 time_filter: str = "month") -> dict:
    """
    Search Reddit for a keyword across target subreddits.

    Returns:
    {
        "keyword": "friend app",
        "total_posts": 12,
        "subreddit_hits": {"makingfriends": 5, "socialskills": 4, "lonely": 3},
        "top_posts": [
            {"title": "...", "subreddit": "...", "score": 42, "url": "...", "num_comments": 15}
        ],
        "pain_signal": True/False  (True if frustration language found)
    }
    """
    subs = subreddits or VALIDATION_SUBS
    all_posts: list[dict] = []
    sub_hits: dict[str, int] = {}

    for sub in subs:
        url = (
            f"https://www.reddit.com/r/{sub}/search.json"
            f"?q={urllib.request.quote(keyword)}"
            f"&restrict_sr=on&sort=relevance&t={time_filter}&limit={limit}"
        )
        req = urllib.request.Request(url, headers=_HEADERS)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            # 429, 403, timeout — skip this sub, don't crash
            print(f"[reddit] {sub}: {e}")
            time.sleep(_REQUEST_DELAY)
            continue

        posts = data.get("data", {}).get("children", [])
        count = len(posts)
        if count > 0:
            sub_hits[sub] = count

        for p in posts:
            pd = p.get("data", {})
            all_posts.append({
                "title":        pd.get("title", ""),
                "subreddit":    sub,
                "score":        pd.get("score", 0),
                "url":          f"https://reddit.com{pd.get('permalink', '')}",
                "num_comments": pd.get("num_comments", 0),
                "created_utc":  pd.get("created_utc", 0),
            })

        time.sleep(_REQUEST_DELAY)

    # Sort by score, keep top posts
    all_posts.sort(key=lambda p: p["score"], reverse=True)
    top = all_posts[:10]

    # Pain signal — look for frustration language in titles
    pain_words = [
        "wish", "need", "looking for", "frustrated", "struggle",
        "lonely", "hard to", "difficult", "impossible", "can't find",
        "where can i", "does anyone know", "alternative to",
        "nothing works", "sick of", "tired of", "help me",
    ]
    pain_signal = any(
        any(pw in p["title"].lower() for pw in pain_words)
        for p in all_posts
    )

    return {
        "keyword":        keyword,
        "total_posts":    len(all_posts),
        "subreddit_hits": sub_hits,
        "top_posts":      top,
        "pain_signal":    pain_signal,
    }


def validate_clusters(clusters: list[dict],
                      max_checks: int = 3) -> list[dict]:
    """
    For the top N clusters, run Reddit validation on the top keyword.
    Mutates clusters in-place, adding 'reddit' field.
    """
    for cluster in clusters[:max_checks]:
        kw = cluster["top_keyword"]
        print(f"[reddit] Checking: {kw}")
        result = check_reddit(kw)
        cluster["reddit"] = result
        print(f"[reddit]   {result['total_posts']} posts across "
              f"{len(result['subreddit_hits'])} subs"
              f"  pain_signal={result['pain_signal']}")

    return clusters


# --- Standalone test ---
if __name__ == "__main__":
    print("Testing Reddit validation for 'friend app'...\n")
    result = check_reddit("friend app")
    print(f"Total posts: {result['total_posts']}")
    print(f"Subreddit hits: {result['subreddit_hits']}")
    print(f"Pain signal: {result['pain_signal']}")
    print(f"\nTop posts:")
    for p in result["top_posts"][:5]:
        print(f"  [{p['subreddit']}] {p['title']}")
        print(f"    score={p['score']}  comments={p['num_comments']}")
        print(f"    {p['url']}")
