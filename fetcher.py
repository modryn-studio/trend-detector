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
# Covers the 5 categories most likely to contain buildable signals.
# Hobbies/Leisure (8) and Jobs/Education (9) were previously dropped for
# noise, but the noise filter in scorer.py handles cultural events — and
# missing these categories means 0 trendspy results if trends shift there.
TOPIC_MAP: dict[int, str] = {
    18: "technology",       # Technology
    3:  "finance",          # Business and Finance
    7:  "health",           # Health
    8:  "hobbies",          # Hobbies & Leisure
    9:  "education",        # Jobs & Education
}

# One client for the lifetime of the process — shares session/cookies
# across both the discovery call and the time-series enrichment calls.
# request_delay=10: trendspy warns to use 10 after repeated 429s; consecutive
# daily runs build IP heat so we need the full recommended delay.
_client = Trends(request_delay=10)


def fetch_trending(geo: str = "US") -> list[dict]:
    """
    Pull all currently trending topics from Google for the given geo.
    Returns a list of dicts with the raw trending data we need for scoring:
      { keyword, category, volume, growth_pct, trend_keywords }

    This is 1 API call. No seeds, no batching, no rate-limit risk.
    """
    trends = _client.trending_now(geo=geo)

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
    series: dict[str, list[float]] = {}

    chunks = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]
    for chunk in chunks:
        for attempt in range(2):  # 1 retry on 429
            try:
                df = _client.interest_over_time(chunk, timeframe=timeframe, geo=geo)
                if df is not None and not df.empty:
                    df = df.drop(columns=["isPartial"], errors="ignore")
                    for kw in chunk:
                        if kw in df.columns:
                            series[kw] = df[kw].tolist()
                break  # success — move to next chunk
            except Exception as e:
                if "429" in str(e) and attempt == 0:
                    print(f"[fetcher] 429 on batch, retrying in 30s...")
                    time.sleep(30)
                else:
                    print(f"[fetcher] interest_over_time failed for {chunk}: {e}")
                    break

        time.sleep(15)  # 15s between batches to cool down the session

    return series
