"""trend_memory.py — multi-day trend persistence tracking

Reads the last N days of signals_YYYY-MM-DD.json and annotates today's
clusters and unclustered items with memory fields:

  days_seen      — how many of the last N days this signal appeared
  trajectory     — "rising" | "stable" | "fading" (recent vs older appearances)
  first_seen     — ISO date string when this signal first appeared in the window
  best_day_score — highest member/item score seen across the window

Annotates in-place; returns the modified signals dict.
Called from pipeline.py after output assembly, before JSON write.
"""

from datetime import date, timedelta
from pathlib import Path
import json

_MEMORY_DAYS = 7


def _build_keyword_history(
    data_dir: Path, today_str: str, days: int
) -> dict[str, list[dict]]:
    """Build keyword -> [{date, score, offset}] lookup from past signals files.

    Excludes today — only historical data is used to annotate today's output.
    """
    today = date.fromisoformat(today_str)
    history: dict[str, list[dict]] = {}

    for offset in range(1, days + 1):
        past_date = today - timedelta(days=offset)
        path = data_dir / f"signals_{past_date.isoformat()}.json"
        if not path.exists():
            continue

        try:
            with open(path) as f:
                signals = json.load(f)
        except Exception:
            continue

        date_str = signals.get("date", past_date.isoformat())

        # Extract from cluster members
        for cluster in signals.get("clusters", []):
            for member in cluster.get("members", []):
                kw = member["keyword"].lower().strip()
                if kw not in history:
                    history[kw] = []
                history[kw].append({
                    "date":   date_str,
                    "score":  member.get("score", 0),
                    "offset": offset,
                })

        # Extract from unclustered
        for item in signals.get("unclustered", []):
            kw = item["keyword"].lower().strip()
            if kw not in history:
                history[kw] = []
            history[kw].append({
                "date":   date_str,
                "score":  item.get("score", 0),
                "offset": offset,
            })

    return history


def _trajectory(offsets: list[int]) -> str:
    """Determine trend direction from day offsets (1=yesterday, N=N days ago).

    Splits the window into recent (last 3 days) vs older (4+ days ago).
    More recent appearances = rising; more older appearances = fading.
    """
    recent = sum(1 for o in offsets if o <= 3)
    older  = sum(1 for o in offsets if o > 3)
    if recent > older:
        return "rising"
    if older > recent:
        return "fading"
    return "stable"


def _memory_for_keywords(
    keywords: list[str], history: dict[str, list[dict]]
) -> dict:
    """Compute memory fields across a set of keywords (e.g. a cluster's members).

    Deduplicates by date — a cluster 'appeared' on a date once regardless of
    how many member keywords matched. Picks the highest-score entry per date.
    """
    matched: list[dict] = []
    for kw in keywords:
        matched.extend(history.get(kw.lower().strip(), []))

    if not matched:
        return {}

    by_date: dict[str, dict] = {}
    for entry in matched:
        d = entry["date"]
        if d not in by_date or entry["score"] > by_date[d]["score"]:
            by_date[d] = entry

    appearances = sorted(by_date.values(), key=lambda e: e["date"])

    return {
        "days_seen":      len(appearances),
        "trajectory":     _trajectory([e["offset"] for e in appearances]),
        "first_seen":     appearances[0]["date"],
        "best_day_score": max(e["score"] for e in appearances),
    }


def annotate(signals: dict, data_dir: Path, days: int = _MEMORY_DAYS) -> dict:
    """Annotate today's clusters and unclustered items with multi-day memory.

    Modifies signals in-place and returns it. Safe to call with no history —
    items with no past appearances simply get no memory field (new signals).
    """
    today_str = signals.get("date", date.today().isoformat())

    try:
        history = _build_keyword_history(data_dir, today_str, days)
    except Exception as exc:
        print(f"[memory] Failed to load history: {exc}")
        return signals

    if not history:
        return signals

    annotated = 0

    # Clusters: match by full member keyword set — any member match counts
    for cluster in signals.get("clusters", []):
        keywords = [m["keyword"] for m in cluster.get("members", [])]
        mem = _memory_for_keywords(keywords, history)
        if mem:
            cluster["memory"] = mem
            annotated += 1

    # Unclustered: match by individual keyword
    for item in signals.get("unclustered", []):
        mem = _memory_for_keywords([item["keyword"]], history)
        if mem:
            item["memory"] = mem
            annotated += 1

    if annotated:
        print(f"[memory] Annotated {annotated} signals with trend history")

    return signals
