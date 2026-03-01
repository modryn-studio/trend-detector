"""
fetcher.py — trend discovery via trendspy

Uses Google's own trending-now data instead of manually seeded queries.
One call returns 400+ currently rising topics with volume, growth %, and
Google's own category labels — no seed tuning required.

For keywords that survive filtering, we pull a 30-day time series
via interest_over_time so scorer.py can compute velocity and freshness.
"""

import time
from trendspy import Trends

# Google's Trending Now topic IDs → our category names.
# Only the topics that reliably contain buildable signals.
# Dropped Hobbies/Leisure (8) and Jobs/Education (9) — too noisy,
# surfaced random cultural events instead of tool-shaped trends.
TOPIC_MAP: dict[int, str] = {
    18: "technology",       # Technology
    3:  "finance",          # Business and Finance
    7:  "health",           # Health
}

# Reverse lookup: our category names → Google topic IDs
CATEGORIES: dict[str, int] = {v: k for k, v in TOPIC_MAP.items()}


def _make_client() -> Trends:
    return Trends(request_delay=2)


def fetch_trending(geo: str = "US") -> list[dict]:
    """
    Pull all currently trending topics from Google for the given geo.
    Returns a list of dicts with the raw trending data we need for scoring:
      { keyword, category, volume, growth_pct, trend_keywords }

    This is 1 API call. No seeds, no batching, no rate-limit risk.
    """
    tr = _make_client()
    trends = tr.trending_now(geo=geo)

    results: list[dict] = []
    for t in trends:
        # Map Google's topic IDs to our categories — skip topics we don't track
        category = None
        for topic_id in (t.topics or []):
            if topic_id in TOPIC_MAP:
                category = TOPIC_MAP[topic_id]
                break
        if category is None:
            continue

        results.append({
            "keyword":        t.keyword,
            "category":       category,
            "volume":         t.volume or 0,
            "growth_pct":     t.volume_growth_pct or 0,
            "trend_keywords": t.trend_keywords or [],
        })

    return results


def fetch_time_series(keywords: list[str], geo: str = "US",
                      timeframe: str = "today 1-m") -> dict[str, list[float]]:
    """
    For a list of keywords, fetch interest_over_time series.
    Returns { keyword: [float, ...] } for each keyword that has data.

    Batches into groups of 5 (Google's limit). Sleeps between batches.
    Only called for keywords that survive noise filtering — typically 10-20,
    so 2-4 API calls max.
    """
    tr = _make_client()
    series: dict[str, list[float]] = {}

    chunks = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]
    for chunk in chunks:
        try:
            df = tr.interest_over_time(chunk, timeframe=timeframe, geo=geo)
            if df is not None and not df.empty:
                df = df.drop(columns=["isPartial"], errors="ignore")
                for kw in chunk:
                    if kw in df.columns:
                        series[kw] = df[kw].tolist()
        except Exception as e:
            print(f"[fetcher] interest_over_time failed for {chunk}: {e}")

        time.sleep(3)

    return series
