"""
pipeline.py — entry point

Fetches rising trends for a category, scores them, and writes the daily JSON.

Cron setup (run once at setup):
  0 6 * * * /path/to/venv/bin/python /path/to/pipeline.py

Manual run (first-time / testing):
  python pipeline.py
  python pipeline.py --category developer-tools

To run all categories in one shot:
  python pipeline.py --all
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fetcher import CATEGORY_SEEDS, fetch_rising_trends
from scorer import score_trend

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_CATEGORY = "ai-tools"


def run(category: str) -> Path | None:
    print(f"[pipeline] category={category} date={date.today().isoformat()}")

    raw_trends = fetch_rising_trends(category)
    if not raw_trends:
        print("[pipeline] Nothing fetched — skipping write.")
        return None

    scored = sorted(
        [s for t in raw_trends if (s := score_trend(t)) is not None],
        key=lambda t: t["score"],
        reverse=True,
    )

    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / f"trends_{date.today().isoformat()}.json"

    # Append to today's file if it already exists (e.g. --all runs multiple categories)
    existing: list[dict] = []
    if out_path.exists():
        with open(out_path) as f:
            existing = json.load(f).get("trends", [])

    combined = sorted(existing + scored, key=lambda t: t["score"], reverse=True)

    with open(out_path, "w") as f:
        json.dump({"date": str(date.today()), "trends": combined}, f, indent=2)

    print(f"[pipeline] {len(scored)} trends written → {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Trend Detector pipeline")
    parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        choices=list(CATEGORY_SEEDS),
        help=f"Category to fetch (default: {DEFAULT_CATEGORY})",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all categories and merge into one output file",
    )
    args = parser.parse_args()

    if args.all:
        for category in CATEGORY_SEEDS:
            try:
                run(category)
            except Exception as e:
                # Isolate per-category failures — one bad category won't kill the others
                print(f"[pipeline] Error in '{category}': {e}")
        _print_summary()
    else:
        run(args.category)


def _print_summary() -> None:
    """Print a per-category breakdown so you can read signal quality at a glance
    without opening the JSON. Run time is ~2s after the pipeline finishes."""
    out_path = DATA_DIR / f"trends_{date.today().isoformat()}.json"
    if not out_path.exists():
        print("[pipeline] No output to summarise.")
        return

    with open(out_path) as f:
        data = json.load(f)

    trends = data.get("trends", [])
    by_category: dict[str, list[dict]] = {}
    for t in trends:
        by_category.setdefault(t["category"], []).append(t)

    print(f"\n[pipeline] Summary — {date.today().isoformat()}")
    for cat in CATEGORY_SEEDS:
        cat_trends = by_category.get(cat, [])
        if not cat_trends:
            print(f"  {cat:<20} 0 trends")
        else:
            avg_score = sum(t["score"] for t in cat_trends) / len(cat_trends)
            top = cat_trends[0]["keyword"]
            print(f"  {cat:<20} {len(cat_trends)} trends  avg={avg_score:.0f}  top='{top}'")


if __name__ == "__main__":
    main()
