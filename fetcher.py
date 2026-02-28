"""
fetcher.py — pytrends wrapper

Pulls rising related queries for a category's seed keywords,
then fetches interest_over_time for each rising keyword so
scorer.py has a time series to work with.

pytrends is a scraping bridge, not an official API. It rate-limits
aggressively, so we sleep between requests and cap batch sizes.
"""

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from pytrends_modern.request import TrendReq

# Seed keywords per category — phrase these as specific frictions, not category names.
# Pain-point phrasing surfaces rising queries from people with a problem.
# Category-level phrasing ("productivity app", "task manager") surfaces informational
# queries ("what is X", "how to use X") — those have no buildable product behind them.
CATEGORY_SEEDS: dict[str, list[str]] = {
    "productivity":    ["too many browser tabs", "can't keep track of tasks", "overwhelmed at work", "project falling through cracks"],
    "ai-tools":        ["AI workflow automation", "AI prompt tool", "AI data extraction", "LLM API wrapper"],
    "developer-tools": ["API keeps breaking", "command line tool", "local dev environment setup", "developer productivity tool"],
    "finance":         ["personal finance app", "budgeting spreadsheet not working", "track spending automatically", "fintech tool"],
    "health":          ["sleep tracker app", "waterproof fitness tracker", "mental health check in app", "nutrition logging app"],
    "creator-tools":   ["repurpose content automatically", "newsletter tool", "short form video scheduler", "social media content tool"],
}


def _make_client() -> TrendReq:
    # retries=1 + tight read timeout so a stalled request fails fast
    # rather than hanging the process until the OS task scheduler kills it
    return TrendReq(hl="en-US", tz=0, timeout=(10, 15), retries=1, backoff_factor=0.3)


def _call(fn, *args, timeout: int = 30, **kwargs):
    """Run fn(*args, **kwargs) with a hard wall-clock timeout.
    Raises FuturesTimeout if it doesn't return in time — caught upstream.
    """
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn, *args, **kwargs)
        return future.result(timeout=timeout)


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
            _call(pytrends.build_payload, batch, timeframe=timeframe, geo="US")
            related = _call(pytrends.related_queries)
            for seed in batch:
                rising_df = related.get(seed, {}).get("rising")
                if rising_df is not None and not rising_df.empty:
                    # top 5 rising queries per seed keeps the list focused
                    for query in rising_df["query"].head(5).tolist():
                        rising_keywords.add(query)
        except FuturesTimeout:
            print(f"[fetcher] Timeout: related_queries stalled for {batch} — skipping")
        except Exception as e:
            print(f"[fetcher] Warning: related_queries failed for {batch}: {e}")

        time.sleep(2)  # avoid 429s — pytrends is a scraper, not an API

    if not rising_keywords:
        print(f"[fetcher] No rising keywords found for '{category}'. Returning empty.")
        return []

    # Drop garbage before hitting the Trends API:
    # - Headlines and test questions come through as rising queries (too long)
    # - Fill-in-the-blank patterns ("______") are quiz content, not search trends
    # - Anything with sentence punctuation is a headline, not a keyword
    def _is_usable(kw: str) -> bool:
        if len(kw) > 60:
            return False
        if "__" in kw or kw.endswith(".") or kw.endswith("?"):
            return False
        return True

    rising_keywords = {kw for kw in rising_keywords if _is_usable(kw)}
    if not rising_keywords:
        print(f"[fetcher] All keywords filtered as garbage for '{category}'. Returning empty.")
        return []

    print(f"[fetcher] Found {len(rising_keywords)} rising keywords for '{category}'")

    # Cap at 10 trends to keep runtime reasonable for a daily cron
    kw_list = list(rising_keywords)[:10]
    results: list[dict] = []

    # Fetch interest_over_time in batches of 5 (pytrends hard limit per payload)
    for i in range(0, len(kw_list), 5):
        batch = kw_list[i : i + 5]
        try:
            _call(pytrends.build_payload, batch, timeframe=timeframe, geo="US")
            iot = _call(pytrends.interest_over_time)
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
        except FuturesTimeout:
            print(f"[fetcher] Timeout: interest_over_time stalled for {batch} — skipping")
        except Exception as e:
            print(f"[fetcher] Warning: interest_over_time failed for {batch}: {e}")

        time.sleep(2)

    return results
