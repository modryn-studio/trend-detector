"""
fetcher.py — pytrends wrapper

Pulls rising related queries for a category's seed keywords,
then fetches interest_over_time for each rising keyword so
scorer.py has a time series to work with.

pytrends is a scraping bridge, not an official API. It rate-limits
aggressively, so we sleep between requests and cap batch sizes.
"""

import time
from pytrends_modern.request import TrendReq

# Seed keywords per category — broad enough to surface related rising queries,
# specific enough to stay on-topic. Expand as you observe noise vs signal.
CATEGORY_SEEDS: dict[str, list[str]] = {
    "productivity":    ["productivity app", "task manager", "automation tool", "workflow software"],
    "ai-tools":        ["AI workflow automation", "AI prompt tool", "AI data extraction", "LLM API wrapper", "AI writing assistant"],
    "developer-tools": ["developer tool", "coding assistant", "API tool", "command line tool"],
    "finance":         ["personal finance app", "budgeting tool", "investing app", "fintech tool"],
    "health":          ["health app", "fitness tracker", "mental health app", "nutrition tracker"],
    "creator-tools":   ["content creation tool", "video editor app", "newsletter tool", "social media tool"],
}


def _make_client() -> TrendReq:
    return TrendReq(hl="en-US", tz=0, timeout=(10, 25), retries=2, backoff_factor=0.5)


def fetch_rising_trends(category: str, timeframe: str = "today 1-m") -> list[dict]:
    """
    Return a list of trend dicts for the given category, each containing:
      { keyword, category, interest_series: list[float] }

    interest_series is daily Google Trends interest (0–100 scale) over
    the timeframe window — used by scorer.py for velocity and freshness.
    """
    seeds = CATEGORY_SEEDS.get(category)
    if not seeds:
        raise ValueError(
            f"Unknown category '{category}'. Valid options: {list(CATEGORY_SEEDS)}"
        )

    pytrends = _make_client()
    rising_keywords: set[str] = set()

    # Fetch rising related queries in batches of 2 to stay under pytrends limits
    for i in range(0, len(seeds), 2):
        batch = seeds[i : i + 2]
        try:
            pytrends.build_payload(batch, timeframe=timeframe, geo="US")
            related = pytrends.related_queries()
            for seed in batch:
                rising_df = related.get(seed, {}).get("rising")
                if rising_df is not None and not rising_df.empty:
                    # top 5 rising queries per seed keeps the list focused
                    for query in rising_df["query"].head(5).tolist():
                        rising_keywords.add(query)
        except Exception as e:
            print(f"[fetcher] Warning: related_queries failed for {batch}: {e}")

        time.sleep(2)  # avoid 429s — pytrends is a scraper, not an API

    if not rising_keywords:
        print(f"[fetcher] No rising keywords found for '{category}'. Returning empty.")
        return []

    print(f"[fetcher] Found {len(rising_keywords)} rising keywords for '{category}'")

    # Cap at 10 trends to keep runtime reasonable for a daily cron
    kw_list = list(rising_keywords)[:10]
    results: list[dict] = []

    # Fetch interest_over_time in batches of 5 (pytrends hard limit per payload)
    for i in range(0, len(kw_list), 5):
        batch = kw_list[i : i + 5]
        try:
            pytrends.build_payload(batch, timeframe=timeframe, geo="US")
            iot = pytrends.interest_over_time()
            if iot.empty:
                continue
            iot = iot.drop(columns=["isPartial"], errors="ignore")
            for kw in batch:
                if kw in iot.columns:
                    results.append(
                        {
                            "keyword": kw,
                            "category": category,
                            "interest_series": iot[kw].tolist(),
                        }
                    )
        except Exception as e:
            print(f"[fetcher] Warning: interest_over_time failed for {batch}: {e}")

        time.sleep(2)

    return results
