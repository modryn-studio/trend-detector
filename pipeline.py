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
            existing = json.load(f)

    combined = sorted(existing + scored, key=lambda t: t["score"], reverse=True)

    with open(out_path, "w") as f:
        json.dump(combined, f, indent=2)

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
            run(category)
    else:
        run(args.category)


if __name__ == "__main__":
    main()
