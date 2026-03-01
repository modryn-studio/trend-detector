"""
pipeline.py — entry point

3-layer trend pipeline:
  Source 1: trendspy       — Google's internal trending API (2-3 calls)
  Source 2: Google RSS     — public feed, stdlib XML parse (1 call)
  Source 3: Gmail ingest   — IMAP + app password, parses newsletter HTML

Usage:
  python pipeline.py              # trendspy only (default, backward compat)
  python pipeline.py --rss        # RSS only
  python pipeline.py --email      # email newsletter only
  python pipeline.py --trendspy   # trendspy only (explicit)
  python pipeline.py --all        # all 3 sources + cross-reference
  python pipeline.py --top 20     # keep top 20 after scoring
  python pipeline.py --no-series  # skip time-series enrichment (faster)
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fetcher import fetch_trending, fetch_time_series
from rss_fetcher import fetch_rss
from email_ingest import fetch_email
from scorer import is_buildable, score_trend

DATA_DIR = Path(__file__).parent / "data"


def _normalize_rss(rss_trends: list[dict]) -> list[dict]:
    """Convert RSS items into the same shape trendspy returns so they
    flow through the same filter → score path."""
    normalized = []
    for t in rss_trends:
        normalized.append({
            "keyword":        t["keyword"],
            "category":       "unknown",       # RSS has no category IDs
            "volume":         t["approx_traffic"],
            "growth_pct":     0,               # RSS has no growth data
            "trend_keywords": [],
            "source":         "rss",
            "related_news":   t.get("related_news", []),
        })
    return normalized


def _parse_growth_pct(growth_str: str) -> float:
    """'+2,900%' → 2900.0, 'breakout' → 5000.0, '' → 0."""
    if not growth_str:
        return 0.0
    if growth_str in ("breakout", "all-time high"):
        return 5000.0  # Treat breakout as maximum growth signal
    raw = growth_str.replace(",", "").replace("+", "").replace("%", "").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _normalize_email(email_trends: list[dict]) -> list[dict]:
    """Convert email-parsed items into the scorer's expected shape."""
    normalized = []
    for t in email_trends:
        normalized.append({
            "keyword":        t["keyword"],
            "category":       t.get("category", "unknown"),
            "volume":         0,                # email has no volume data
            "growth_pct":     _parse_growth_pct(t.get("growth", "")),
            "trend_keywords": [],
            "source":         "email",
        })
    return normalized


def _collect(sources: list[str]) -> list[dict]:
    """Fetch from requested sources and return a unified list."""
    all_trends: list[dict] = []

    if "trendspy" in sources:
        print("[pipeline] Fetching from trendspy...")
        ts = fetch_trending()
        # Tag source for cross-reference (issue #5)
        for t in ts:
            t.setdefault("source", "trendspy")
        print(f"[pipeline]   trendspy: {len(ts)} trends in tracked categories")
        all_trends.extend(ts)

    if "rss" in sources:
        print("[pipeline] Fetching from RSS...")
        rss = fetch_rss()
        rss_norm = _normalize_rss(rss)
        print(f"[pipeline]   rss: {len(rss_norm)} trends")
        all_trends.extend(rss_norm)

    if "email" in sources:
        print("[pipeline] Fetching from email...")
        email_trends = fetch_email(mark_read=False)
        email_norm = _normalize_email(email_trends)
        print(f"[pipeline]   email: {len(email_norm)} trends")
        all_trends.extend(email_norm)

    return all_trends


def _cross_reference(trends: list[dict]) -> list[dict]:
    """Group trends by normalized keyword across sources.

    Merges data from multiple sources into one record per keyword:
    - Keeps the highest volume and growth_pct seen
    - Tracks which sources reported each keyword
    - Preserves the best category (trendspy > email > rss)
    """
    groups: dict[str, dict] = {}

    # Source priority for category — higher is better
    _SRC_RANK = {"trendspy": 3, "email": 2, "rss": 1}

    for t in trends:
        key = t["keyword"].lower().strip()
        source = t.get("source", "unknown")

        if key not in groups:
            groups[key] = {
                "keyword":        t["keyword"],
                "category":       t["category"],
                "volume":         t["volume"],
                "growth_pct":     t["growth_pct"],
                "trend_keywords": t.get("trend_keywords", []),
                "sources":        [source],
                "source_count":   1,
                "related_news":   t.get("related_news", []),
                "_src_rank":      _SRC_RANK.get(source, 0),
            }
        else:
            g = groups[key]
            if source not in g["sources"]:
                g["sources"].append(source)
                g["source_count"] += 1
            # Keep highest volume and growth
            g["volume"] = max(g["volume"], t["volume"])
            g["growth_pct"] = max(g["growth_pct"], t["growth_pct"])
            # Keep best category
            rank = _SRC_RANK.get(source, 0)
            if rank > g["_src_rank"] and t["category"] != "unknown":
                g["category"] = t["category"]
                g["_src_rank"] = rank
            # Merge related news
            g["related_news"].extend(t.get("related_news", []))
            # Merge trend keywords
            g["trend_keywords"].extend(t.get("trend_keywords", []))

    # Clean up internal field
    for g in groups.values():
        del g["_src_rank"]

    return list(groups.values())


def run(sources: list[str], top_n: int = 15,
        skip_series: bool = False) -> Path | None:
    today = date.today().isoformat()
    print(f"[pipeline] date={today}  sources={sources}")

    # --- Stage 1: Collect from sources ---
    raw = _collect(sources)

    if not raw:
        print("[pipeline] Nothing found — skipping write.")
        return None

    # Cross-reference if multiple sources
    multi_source = len(sources) > 1
    if multi_source:
        before = len(raw)
        raw = _cross_reference(raw)
        merged = before - len(raw)
        multi_hits = sum(1 for t in raw if t.get("source_count", 1) > 1)
        print(f"[pipeline] Cross-referenced: {before} → {len(raw)} unique"
              f" ({multi_hits} multi-source)")

    # --- Stage 2: Filter noise ---
    filtered = [t for t in raw if is_buildable(t["keyword"])]
    print(f"[pipeline] {len(filtered)} trends after noise filter")

    if not filtered:
        print("[pipeline] Everything filtered — skipping write.")
        return None

    # --- Stage 3: Quick-score (no API calls) ---
    scored = [score_trend(t) for t in filtered]

    # Apply multi-source confidence boost
    if multi_source:
        for t in scored:
            sc = t.get("source_count", 1)
            if sc >= 3:
                t["score"] = min(100, t["score"] + 40)
            elif sc >= 2:
                t["score"] = min(100, t["score"] + 20)

    scored.sort(key=lambda t: t["score"], reverse=True)

    # Keep only top N for time-series enrichment
    top = scored[:top_n]

    # --- Stage 4: Enrich with time series (2-4 API calls) ---
    if not skip_series and "trendspy" in sources:
        keywords = [t["keyword"] for t in top]
        print(f"[pipeline] Fetching time series for {len(keywords)} keywords...")
        series_map = fetch_time_series(keywords)
        print(f"[pipeline] Got series for {len(series_map)}/{len(keywords)} keywords")

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

    # signals_ for multi-source, trends_ for single-source
    prefix = "signals" if multi_source else "trends"
    out_path = DATA_DIR / f"{prefix}_{today}.json"

    # Add source list to each trend for the output
    output_trends = []
    for t in top:
        entry = dict(t)
        # Include sources list if cross-referencing
        if multi_source:
            # Find the merged raw record to get the sources list
            raw_rec = next(
                (r for r in raw if r["keyword"].lower() == t["keyword"].lower()),
                None,
            )
            if raw_rec and "sources" in raw_rec:
                entry["sources"] = raw_rec["sources"]
        output_trends.append(entry)

    with open(out_path, "w") as f:
        json.dump({"date": today, "trends": output_trends}, f, indent=2)

    print(f"[pipeline] {len(output_trends)} trends written → {out_path}")
    _print_summary(output_trends)
    return out_path


def _print_summary(trends: list[dict]) -> None:
    """Top 5 signals for quick morning scanning."""
    today = date.today().isoformat()
    print(f"\n  === Top Signals ({today}) ===\n")
    for i, t in enumerate(trends[:5], 1):
        parts = [f"score={t['score']}"]
        # Sources
        sources = t.get("sources", [t.get("source", "?")])
        sc = t.get("source_count", 1)
        parts.append(f"sources={sc}")
        # Growth
        growth_pct = t.get("_raw", {}).get("google_growth_pct", 0)
        if growth_pct >= 5000:
            parts.append("growth=breakout")
        elif growth_pct > 0:
            parts.append(f"growth=+{growth_pct:.0f}%")
        # Volume
        vol = t.get("_raw", {}).get("google_volume", 0)
        if vol >= 100_000:
            parts.append(f"traffic={vol // 1000}K+")
        elif vol >= 1_000:
            parts.append(f"traffic={vol // 1000}K+")
        elif vol > 0:
            parts.append(f"traffic={vol}")

        info = "  ".join(parts)
        src_list = ",".join(sources)
        print(f"  {i}. {t['keyword']:<35} {info}")
        print(f"     [{src_list}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trend Detector pipeline")

    # Source selection — mutually exclusive group
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--trendspy", action="store_true",
                     help="trendspy source only")
    src.add_argument("--rss", action="store_true",
                     help="RSS feed source only")
    src.add_argument("--email", action="store_true",
                     help="Email newsletter source only")
    src.add_argument("--all", action="store_true",
                     help="All 3 sources + cross-reference")

    parser.add_argument("--top", type=int, default=15,
                        help="Top N trends to keep (default: 15)")
    parser.add_argument("--no-series", action="store_true",
                        help="Skip time-series enrichment (faster)")

    args = parser.parse_args()

    # Determine which sources to run
    if args.all:
        sources = ["trendspy", "rss", "email"]
    elif args.rss:
        sources = ["rss"]
    elif args.email:
        sources = ["email"]
    else:
        # Default: trendspy only (backward compat)
        sources = ["trendspy"]

    run(sources=sources, top_n=args.top, skip_series=args.no_series)


if __name__ == "__main__":
    main()
