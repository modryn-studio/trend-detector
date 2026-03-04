"""
pipeline.py — entry point

3-layer trend pipeline:
  Source 1: trendspy       — Google's internal trending API (2-3 calls)
  Source 2: Google RSS     — public feed, stdlib XML parse (1 call)
  Source 3: Gmail ingest   — IMAP + app password, parses newsletter HTML

Usage:
  python pipeline.py              # all 3 sources + cross-reference (default)
  python pipeline.py --trendspy   # trendspy only
  python pipeline.py --rss        # RSS only
  python pipeline.py --email      # email newsletter only
  python pipeline.py --top 20         # keep top 20 after scoring
  python pipeline.py --no-email       # trendspy + RSS only (skip newsletter)
  python pipeline.py --no-series      # skip time-series enrichment (faster)
  python pipeline.py --no-competitor  # skip competitor check (faster)
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fetcher import fetch_trending, fetch_time_series
from rss_fetcher import fetch_rss
from email_ingest import fetch_email
from scorer import is_buildable, score_trend
from cluster import detect_clusters, get_unclustered
from reddit_check import validate_clusters
from competitor_check import validate_build_opportunities
from reporter import write_briefing
from trend_memory import annotate as annotate_memory

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
                "source":         source,
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
            # Keep best category and highest-priority source label
            rank = _SRC_RANK.get(source, 0)
            if rank > g["_src_rank"]:
                if t["category"] != "unknown":
                    g["category"] = t["category"]
                g["source"] = source
                g["_src_rank"] = rank
            # Merge related news
            g["related_news"].extend(t.get("related_news", []))
            # Merge trend keywords
            g["trend_keywords"].extend(t.get("trend_keywords", []))

    # Clean up internal field
    for g in groups.values():
        del g["_src_rank"]

    return list(groups.values())


def _persist_decisions(output: dict, out_path: Path) -> None:
    """Re-write signals JSON with decision data attached during briefing.

    _decision_section attaches _decision dicts (including context_seed)
    to cluster/unclustered dicts via mutation. This writes them to disk
    under a top-level "decisions" key so the build phase can pull them.
    """
    decisions = {}
    for c in output.get("clusters", []):
        d = c.pop("_decision", None)
        # Clean up transient render fields so JSON stays canonical
        c.pop("display_name", None)
        c.pop("original_name", None)
        if d:
            decisions[c["cluster_name"]] = d
    for t in output.get("unclustered", []):
        d = t.pop("_decision", None)
        if d:
            decisions[t["keyword"]] = d

    if decisions:
        output["decisions"] = decisions
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"[pipeline] Decisions persisted ({len(decisions)} entries)")


def run(sources: list[str], top_n: int = 15,
        skip_series: bool = False, skip_reddit: bool = False,
        skip_competitor: bool = False) -> Path | None:
    today = date.today().isoformat()
    print(f"[pipeline] date={today}  sources={sources}")

    # --- Stage 1: Collect from sources ---
    raw = _collect(sources)

    if not raw:
        print("[pipeline] Nothing found -- skipping write.")
        return None

    # Cross-reference if multiple sources
    multi_source = len(sources) > 1
    if multi_source:
        before = len(raw)
        raw = _cross_reference(raw)
        merged = before - len(raw)
        multi_hits = sum(1 for t in raw if t.get("source_count", 1) > 1)
        print(f"[pipeline] Cross-referenced: {before} -> {len(raw)} unique"
              f" ({multi_hits} multi-source)")

    # --- Stage 2: Filter noise ---
    filtered = [t for t in raw if is_buildable(t["keyword"])]
    print(f"[pipeline] {len(filtered)} trends after noise filter")

    if not filtered:
        print("[pipeline] Everything filtered -- skipping write.")
        return None

    # --- Stage 3: Score ALL filtered trends (not just top N) ---
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

    # --- Stage 4: Cluster detection ---
    clusters = detect_clusters(scored)
    unclustered = get_unclustered(scored, clusters)
    print(f"[pipeline] Found {len(clusters)} clusters, "
          f"{len(unclustered)} unclustered trends")

    # --- Stage 5: Reddit validation on top clusters ---
    if not skip_reddit and clusters:
        print("[pipeline] Validating top clusters against Reddit...")
        validate_clusters(clusters, max_checks=3)

    # --- Stage 5.5: Competitor check ---
    competition = {}
    if not skip_competitor and clusters:
        print("[pipeline] Running competitor checks...")
        competition = validate_build_opportunities(
            clusters, unclustered, max_checks=5
        )

    # --- Stage 6: Enrich top keywords with time series ---
    # Collect top keywords for enrichment: cluster tops + unclustered tops
    enrich_keywords = []
    for c in clusters[:5]:
        enrich_keywords.append(c["top_keyword"])
    for t in unclustered[:top_n]:
        if t["keyword"] not in enrich_keywords:
            enrich_keywords.append(t["keyword"])
    enrich_keywords = enrich_keywords[:top_n]

    if not skip_series and "trendspy" in sources and enrich_keywords:
        print(f"[pipeline] Fetching time series for {len(enrich_keywords)} keywords...")
        series_map = fetch_time_series(enrich_keywords)
        print(f"[pipeline] Got series for {len(series_map)}/{len(enrich_keywords)} keywords")

        # Re-score enriched keywords with freshness data
        for c in clusters:
            for i, m in enumerate(c["members"]):
                series = series_map.get(m["keyword"])
                if series:
                    raw_trend = next(
                        (r for r in filtered if r["keyword"] == m["keyword"]), None
                    )
                    if raw_trend:
                        c["members"][i] = score_trend(raw_trend, series=series)

        for i, t in enumerate(unclustered):
            series = series_map.get(t["keyword"])
            if series:
                raw_trend = next(
                    (r for r in filtered if r["keyword"] == t["keyword"]), None
                )
                if raw_trend:
                    unclustered[i] = score_trend(raw_trend, series=series)

        # Re-sort clusters after enrichment so top_keyword and cluster_score
        # reflect the updated member scores
        for c in clusters:
            c["members"].sort(key=lambda m: m["score"], reverse=True)
            if c["members"]:
                top = c["members"][0]
                c["top_keyword"] = top["keyword"]
                avg = sum(m["score"] for m in c["members"]) / len(c["members"])
                n = len(c["members"])
                size_bonus = min(25, n * 3)
                growth_bonus = min(
                    15,
                    sum(
                        1 for m in c["members"]
                        if m.get("_raw", {}).get("google_growth_pct", 0) >= 200
                    ) * 5,
                )
                c["cluster_score"] = min(100, round(avg + size_bonus + growth_bonus))
        clusters.sort(key=lambda c: c["cluster_score"], reverse=True)

    # --- Stage 7: Write output ---
    DATA_DIR.mkdir(exist_ok=True)

    out_path = DATA_DIR / f"signals_{today}.json"

    output = {
        "date": today,
        "sources": sources,
        "clusters": [],
        "unclustered": [],
        "competition": competition if competition else {},
    }

    for c in clusters:
        cluster_out = {
            "cluster_name":   c["cluster_name"],
            "cluster_score":  c["cluster_score"],
            "member_count":   c["member_count"],
            "top_keyword":    c["top_keyword"],
            "growth_signals": c["growth_signals"],
            "members":        c["members"],
        }
        # Include Reddit validation if present
        if "reddit" in c:
            r = c["reddit"]
            cluster_out["reddit"] = {
                "total_posts":    r["total_posts"],
                "subreddit_hits": r["subreddit_hits"],
                "pain_signal":    r["pain_signal"],
                "pain_reliable":  r.get("pain_reliable", False),
                "keyword":        r.get("keyword", c["top_keyword"]),
                "top_posts":      r["top_posts"][:5],
            }
        output["clusters"].append(cluster_out)

    # Top unclustered (individual signals)
    unclustered.sort(key=lambda t: t["score"], reverse=True)
    output["unclustered"] = unclustered[:top_n]

    # Annotate with multi-day trend memory (no-op if no history exists yet)
    annotate_memory(output, DATA_DIR)

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    total = sum(c["member_count"] for c in clusters) + len(output["unclustered"])
    print(f"[pipeline] {len(clusters)} clusters + {len(output['unclustered'])} "
          f"unclustered written -> {out_path}")
    _print_summary(clusters, output["unclustered"])

    # --- Stage 8: Generate briefing ---
    # Wrap so a briefing bug never loses a successful data run
    try:
        briefing_path = write_briefing(output, today, competition=competition)
        print(f"[pipeline] Briefing written -> {briefing_path}")

        # Re-write JSON with decision data (including context_seed)
        # that was attached to cluster/unclustered dicts during briefing generation
        _persist_decisions(output, out_path)
    except Exception as exc:  # noqa: BLE001
        print(f"[pipeline] Briefing generation failed (data saved): {exc}")

    return out_path


def _print_summary(clusters: list[dict], unclustered: list[dict]) -> None:
    """Morning-ready summary: clusters first, then top individual signals."""
    today = date.today().isoformat()

    if clusters:
        print(f"\n  === MACRO TRENDS ({today}) ===\n")
        for i, c in enumerate(clusters, 1):
            reddit_tag = ""
            if "reddit" in c:
                r = c["reddit"]
                if r["pain_signal"]:
                    reddit_tag = "  !! PAIN SIGNAL"
                elif r["total_posts"] > 0:
                    reddit_tag = f"  ({r['total_posts']} Reddit posts)"

            print(f"  {i}. [{c['cluster_score']}] {c['cluster_name'].upper()}"
                  f"  ({c['member_count']} keywords){reddit_tag}")

            for m in sorted(c["members"], key=lambda m: m["score"], reverse=True)[:5]:
                gpct = m.get("_raw", {}).get("google_growth_pct", 0)
                if gpct >= 5000:
                    growth = "breakout"
                elif gpct >= 200:
                    growth = f"+{gpct:.0f}%"
                else:
                    growth = ""
                marker = f"  [{growth}]" if growth else ""
                print(f"       - {m['keyword']}{marker}")

            if c.get("growth_signals"):
                print(f"       Growth: {', '.join(c['growth_signals'][:3])}")

    if unclustered:
        print(f"\n  === INDIVIDUAL SIGNALS ===\n")
        for i, t in enumerate(unclustered[:10], 1):
            gpct = t.get("_raw", {}).get("google_growth_pct", 0)
            if gpct >= 5000:
                growth = "breakout"
            elif gpct > 0:
                growth = f"+{gpct:.0f}%"
            else:
                growth = ""
            src = t.get("source", "?")
            info = f"score={t['score']}  [{src}]"
            if growth:
                info += f"  {growth}"
            print(f"  {i}. {t['keyword']:<40} {info}")


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
                     help="All 3 sources + cross-reference (default)")

    parser.add_argument("--top", type=int, default=15,
                        help="Top N trends to keep (default: 15)")
    parser.add_argument("--no-email", action="store_true",
                        help="Exclude email newsletter source (trendspy + RSS only)")
    parser.add_argument("--no-series", action="store_true",
                        help="Skip time-series enrichment (faster)")
    parser.add_argument("--no-reddit", action="store_true",
                        help="Skip Reddit validation (faster)")
    parser.add_argument("--no-competitor", action="store_true",
                        help="Skip competitor check (faster)")

    args = parser.parse_args()

    # Determine which sources to run
    if args.all:
        sources = ["trendspy", "rss", "email"]
    elif args.trendspy:
        sources = ["trendspy"]
    elif args.rss:
        sources = ["rss"]
    elif args.email:
        sources = ["email"]
    else:
        # Default: all 3 sources (--no-email removes newsletter)
        sources = ["trendspy", "rss"] if args.no_email else ["trendspy", "rss", "email"]

    run(sources=sources, top_n=args.top, skip_series=args.no_series,
        skip_reddit=args.no_reddit, skip_competitor=args.no_competitor)


if __name__ == "__main__":
    main()
