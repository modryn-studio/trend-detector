"""
pipeline.py — entry point

Fetches currently trending topics from Google, filters noise, scores
what's left, optionally enriches top results with time-series data,
and writes the daily JSON.

  python pipeline.py              # run with defaults
  python pipeline.py --top 20     # score top 20 after filtering
  python pipeline.py --no-series  # skip time-series enrichment (faster)
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fetcher import fetch_trending, fetch_time_series, TOPIC_MAP
from scorer import is_buildable, score_trend

DATA_DIR = Path(__file__).parent / "data"


def run(top_n: int = 15, skip_series: bool = False) -> Path | None:
    today = date.today().isoformat()
    print(f"[pipeline] date={today}")

    # --- Stage 1: Discover (1 API call) ---
    print("[pipeline] Fetching trending topics...")
    raw = fetch_trending()
    print(f"[pipeline] {len(raw)} trends in tracked categories")

    if not raw:
        print("[pipeline] Nothing found — skipping write.")
        return None

    # --- Stage 2: Filter noise ---
    filtered = [t for t in raw if is_buildable(t["keyword"])]
    print(f"[pipeline] {len(filtered)} trends after noise filter")

    if not filtered:
        print("[pipeline] Everything filtered — skipping write.")
        return None

    # --- Stage 3: Quick-score (no API calls) ---
    scored = [score_trend(t) for t in filtered]
    scored.sort(key=lambda t: t["score"], reverse=True)

    # Keep only top N for time-series enrichment
    top = scored[:top_n]

    # --- Stage 4: Enrich with time series (2-4 API calls) ---
    if not skip_series:
        keywords = [t["keyword"] for t in top]
        print(f"[pipeline] Fetching time series for {len(keywords)} keywords...")
        series_map = fetch_time_series(keywords)
        print(f"[pipeline] Got series for {len(series_map)}/{len(keywords)} keywords")

        # Re-score with time series data for better freshness
        enriched = []
        for t in top:
            raw_trend = next(
                (r for r in filtered if r["keyword"] == t["keyword"]), None
            )
            if raw_trend:
                series = series_map.get(t["keyword"])
                enriched.append(score_trend(raw_trend, series=series))
            else:
                enriched.append(t)

        top = sorted(enriched, key=lambda t: t["score"], reverse=True)

    # --- Stage 5: Write output ---
    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / f"trends_{today}.json"

    with open(out_path, "w") as f:
        json.dump({"date": today, "trends": top}, f, indent=2)

    print(f"[pipeline] {len(top)} trends written → {out_path}")
    _print_summary(top)
    return out_path


def _print_summary(trends: list[dict]) -> None:
    """Per-category breakdown for quick scanning."""
    by_cat: dict[str, list[dict]] = {}
    for t in trends:
        by_cat.setdefault(t["category"], []).append(t)

    print(f"\n{'Category':<20} {'Count':>5}  {'Avg':>4}  Top keyword")
    print("-" * 65)
    for cat in sorted(by_cat):
        items = by_cat[cat]
        avg = sum(t["score"] for t in items) / len(items)
        top_kw = items[0]["keyword"]
        print(f"  {cat:<18} {len(items):>5}  {avg:>4.0f}  {top_kw}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trend Detector pipeline")
    parser.add_argument(
        "--top", type=int, default=15,
        help="Number of top trends to keep after scoring (default: 15)",
    )
    parser.add_argument(
        "--no-series", action="store_true",
        help="Skip time-series enrichment (faster, less accurate freshness)",
    )
    args = parser.parse_args()
    run(top_n=args.top, skip_series=args.no_series)


if __name__ == "__main__":
    main()
