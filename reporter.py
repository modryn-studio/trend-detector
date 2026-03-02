"""
reporter.py — daily briefing generator

Reads today's signals JSON and writes a plain-English markdown briefing
to briefings/briefing_YYYY-MM-DD.md.

Rule-based reasoning — no LLM. Logic:
  1. Cluster table: what's trending, ranked
  2. Macro-theme detection: are multiple clusters covering the same underlying need?
  3. Build opportunities: which signals translate to something you can actually ship?
  4. Reddit validation: is the pain real, or did the search hit noise?

Usage:
  python reporter.py                    # uses today's signals file
  python reporter.py --date 2026-03-01  # specific date
"""

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

DATA_DIR    = Path(__file__).parent / "data"
BRIEFING_DIR = Path(__file__).parent / "briefings"

# Clusters whose names look like token-based fallbacks ("gold / future / stock")
# vs. Google editorial names ("Making Friends"). We use this to detect
# whether Google itself grouped these searches as a coherent theme.
_GENERIC_CLUSTER_NAMES = {"top trends", "top searches", "trending", "top topics"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_editorial_cluster(cluster: dict) -> bool:
    """Return True if the cluster name came from a Google Trends newsletter
    section header (Pass 1 clustering) vs. a token-based fallback name."""
    name = cluster["cluster_name"]
    # Token-based names from Pass 2 always contain " / "
    if " / " in name:
        return False
    if name.lower() in _GENERIC_CLUSTER_NAMES:
        return False
    return True


def _breakout_kws(cluster: dict) -> list[str]:
    """Return clean breakout keywords from a cluster (no truncated phrases)."""
    return [
        m["keyword"] for m in cluster["members"]
        if m.get("_raw", {}).get("google_growth_pct", 0) >= 5000
        and "..." not in m["keyword"]
        and "\u2026" not in m["keyword"]
    ]


def _growth_label(pct: float) -> str:
    """Human-readable growth label."""
    if pct >= 5000:
        return "breakout"
    if pct >= 1000:
        return f"+{int(pct):,}%"
    if pct >= 100:
        return f"+{int(pct)}%"
    return ""


def _hot_signals(cluster: dict) -> str:
    """Comma-separated list of the top growth signals for the table."""
    parts = []
    for m in cluster["members"]:
        g = m.get("_raw", {}).get("google_growth_pct", 0)
        label = _growth_label(g)
        if label and "..." not in m["keyword"] and "\u2026" not in m["keyword"]:
            parts.append(f'"{m["keyword"]}" {label}')
        if len(parts) >= 4:
            break
    return ", ".join(parts) if parts else "—"


def _total_breakouts(clusters: list[dict]) -> int:
    return sum(len(_breakout_kws(c)) for c in clusters)


def _stem(word: str) -> str:
    """Minimal suffix stemming — same logic as cluster.py."""
    w = word.lower()
    for suffix in ("ing", "ies", "ed", "er", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[: -len(suffix)]
    return w


def _meaningful_stems(text: str) -> set[str]:
    """Tokenise + stem, removing stopwords."""
    stop = {
        "a", "an", "the", "to", "for", "of", "in", "how", "is", "are",
        "i", "my", "do", "can", "near", "me", "with", "at", "on", "as",
        "be", "and", "or", "what", "where", "why", "when", "who", "that",
        "this", "it", "if", "from", "by", "up", "out", "so", "no", "not",
        "any", "all", "get", "about",
    }
    words = re.findall(r"[a-z]+", text.lower())
    return {_stem(w) for w in words if w not in stop and len(w) > 2}


def _find_editorial_group(clusters: list[dict], top_n: int = 7) -> list[int]:
    """Return indices of editorial clusters in the top N rankings.

    An 'editorial' cluster has a name that came from a Google Trends newsletter
    section header (Pass 1 clustering) — meaning Google's editorial team chose
    to surface this theme. Token-based fallback clusters contain ' / '.

    We group ALL editorial clusters together: when Google dedicates multiple
    newsletter sections in the same week, that is itself the signal — regardless
    of whether the topics share surface-level keywords.
    """
    return [
        i for i, c in enumerate(clusters[:top_n])
        if _is_editorial_cluster(c)
    ]


def _shared_stems(clusters: list[dict], indices: list[int]) -> list[str]:
    """Find stems common to 2+ of the given clusters (member keywords)."""
    stem_sets = []
    for i in indices:
        c = clusters[i]
        all_text = " ".join(m["keyword"] for m in c["members"])
        stem_sets.append(_meaningful_stems(all_text))

    if len(stem_sets) < 2:
        return []

    # Count how many clusters each stem appears in
    counter: Counter = Counter()
    for s in stem_sets:
        for stem in s:
            counter[stem] += 1

    # Return stems shared by at least 2 clusters, sorted by frequency
    shared = [stem for stem, count in counter.most_common() if count >= 2]
    return shared[:6]


def _load_signals(date_str: str | None = None) -> tuple[dict, str]:
    """Load the signals JSON for a given date (default: today).
    Returns (signals_dict, date_str).
    """
    if date_str is None:
        date_str = date.today().isoformat()

    # Try signals first (multi-source), then trends (single-source)
    for prefix in ("signals", "trends"):
        path = DATA_DIR / f"{prefix}_{date_str}.json"
        if path.exists():
            with open(path) as f:
                return json.load(f), date_str

    raise FileNotFoundError(
        f"No signals or trends file found for {date_str} in {DATA_DIR}"
    )


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def _cluster_table_section(clusters: list[dict], unclustered: list[dict]) -> str:
    lines = [
        "## Today's Clusters",
        "",
        "| Rank | Cluster | Score | Hot signals |",
        "|------|---------|-------|-------------|",
    ]
    for i, c in enumerate(clusters, 1):
        lines.append(
            f"| {i} | {c['cluster_name']} | {c['cluster_score']} "
            f"| {_hot_signals(c)} |"
        )
    lines.append("")

    # Notable unclustered (score >= 50 or breakout)
    notable = [
        t for t in unclustered
        if t["score"] >= 50
        or t.get("_raw", {}).get("google_growth_pct", 0) >= 1000
    ]
    if notable:
        parts = []
        for t in notable[:5]:
            g = t.get("_raw", {}).get("google_growth_pct", 0)
            label = _growth_label(g)
            entry = f"**{t['keyword']}** (score {t['score']}"
            if label:
                entry += f", {label}"
            entry += ")"
            parts.append(entry)
        lines.append("Unclustered: " + " · ".join(parts))
        lines.append("")

    return "\n".join(lines)


def _story_section(
    clusters: list[dict],
    editorial_group: list[int],
    shared: list[str],
) -> str:
    lines = ["## The Story", ""]

    total_breakouts = _total_breakouts(clusters)
    top_cluster = clusters[0] if clusters else None

    # --- Macro-theme: multiple editorial clusters ---
    if len(editorial_group) >= 2:
        group_clusters = [clusters[i] for i in editorial_group]
        names = [c["cluster_name"] for c in group_clusters]
        group_breakouts = _total_breakouts(group_clusters)

        # Format: "Clusters X, Y, and Z"
        if len(names) == 2:
            cluster_list = f"**{names[0]}** and **{names[1]}**"
        else:
            cluster_list = (
                ", ".join(f"**{n}**" for n in names[:-1])
                + f", and **{names[-1]}**"
            )

        lines.append(
            f"{len(editorial_group)} of today's top clusters came directly from "
            f"Google's Trends newsletter sections this week: {cluster_list}."
        )
        lines.append(
            "Google's editorial team chose to write about each of these separately. "
            "That grouping is the signal — look at what they have in common."
        )
        lines.append("")

        if group_breakouts >= 5:
            lines.append(
                f"{group_breakouts} keywords across these clusters hit **breakout** "
                f"simultaneously. That's not noise."
            )
        elif group_breakouts >= 2:
            lines.append(
                f"{group_breakouts} keywords across these clusters hit **breakout** "
                f"in the same period."
            )
        lines.append("")

        # If shared stems exist, name the through-line
        if shared:
            lines.append(
                f"Shared concepts across cluster member keywords: "
                f"**{', '.join(shared[:4])}**. "
                f"That's the through-line. Each cluster is a different search "
                f"angle on the same underlying thing."
            )
            lines.append("")
            lines.append("**Each cluster is a different angle on the same question:**")
            lines.append("")
            for c in group_clusters:
                bo = _breakout_kws(c)
                example = f'"{bo[0]}"' if bo else f'"{c["members"][0]["keyword"]}"'
                lines.append(f"- **{c['cluster_name']}** — {example}")
            lines.append("")
        else:
            # Shared stems < threshold — clusters may be separate themes
            lines.append(
                "These clusters don't share many surface-level keywords, so they "
                "may represent separate themes that happened to peak together. "
                "Review each cluster independently."
            )
            lines.append("")

    # --- Single dominant cluster ---
    elif top_cluster and top_cluster["cluster_score"] >= 80:
        bo = _breakout_kws(top_cluster)
        lines.append(
            f"**{top_cluster['cluster_name']}** is the dominant signal today "
            f"(score {top_cluster['cluster_score']}, "
            f"{top_cluster['member_count']} keywords"
            f"{f', {len(bo)} breakout' if bo else ''})."
        )
        lines.append("")

    # --- General summary ---
    lines.append(
        f"**Total today:** {len(clusters)} clusters, "
        f"{total_breakouts} breakout keywords across all signals."
    )
    lines.append("")

    return "\n".join(lines)


def _best_fast_build(
    clusters: list[dict], unclustered: list[dict]
) -> dict | None:
    """Find the single most actionable fast-build keyword.

    Criteria: buildability=high, score >= 55, breakout or strong growth,
    2-5 clean words, not a truncated phrase.
    """
    candidates = []

    # Check unclustered first (already independent signals)
    for t in unclustered:
        g = t.get("_raw", {}).get("google_growth_pct", 0)
        words = t["keyword"].split()
        if (
            t.get("buildability") == "high"
            and t["score"] >= 55
            and g >= 200
            and 2 <= len(words) <= 5
            and "..." not in t["keyword"]
            and "\u2026" not in t["keyword"]
        ):
            candidates.append({"keyword": t["keyword"], "score": t["score"],
                                "growth": g, "cluster": None})

    # Check cluster members
    for c in clusters:
        for m in c["members"]:
            g = m.get("_raw", {}).get("google_growth_pct", 0)
            words = m["keyword"].split()
            if (
                m.get("buildability") == "high"
                and m["score"] >= 55
                and g >= 5000
                and 2 <= len(words) <= 5
                and "..." not in m["keyword"]
                and "\u2026" not in m["keyword"]
            ):
                candidates.append({"keyword": m["keyword"], "score": m["score"],
                                    "growth": g, "cluster": c["cluster_name"]})

    if not candidates:
        return None
    candidates.sort(key=lambda x: (x["growth"], x["score"]), reverse=True)
    return candidates[0]


def _build_section(
    clusters: list[dict],
    unclustered: list[dict],
    editorial_group: list[int],
) -> str:
    lines = ["## Build Opportunities", ""]

    fast = _best_fast_build(clusters, unclustered)
    top = clusters[0] if clusters else None
    group_clusters = [clusters[i] for i in editorial_group] if len(editorial_group) >= 2 else None

    # --- Option A: fastest build ---
    if fast:
        g_label = _growth_label(fast["growth"])
        scope = "1–2 day build. Pure logic, no backend needed." if len(fast["keyword"].split()) <= 4 else "Weekend project."
        context = f" (from cluster: {fast['cluster']})" if fast["cluster"] else ""
        lines.append(f"### Option A — Fastest build")
        lines.append("")
        lines.append(
            f'**"{fast["keyword"]}"** — {g_label}{context}'
        )
        lines.append("")
        lines.append(
            f"This search query has a completely clear use case. "
            f"The person knows exactly what they want; there's no ambiguity in the intent. "
            f"{scope} "
            f"The query is specific enough that you'd rank for it quickly with no competition "
            f"in that exact framing."
        )
        lines.append("")

    # --- Option B: biggest signal ---
    lines.append("### Option B — Biggest signal")
    lines.append("")

    if group_clusters and len(group_clusters) >= 2:
        names = [c["cluster_name"] for c in group_clusters]
        total_members = sum(c["member_count"] for c in group_clusters)
        total_bo = _total_breakouts(group_clusters)

        if len(names) == 2:
            name_str = f"{names[0]} / {names[1]}"
        else:
            name_str = " / ".join(names)

        lines.append(f"**{name_str}** — {total_members} keywords, {total_bo} breakout")
        lines.append("")

        bo_examples = []
        for c in group_clusters:
            bo_examples.extend(_breakout_kws(c)[:2])

        if bo_examples:
            quoted = ", ".join(f'"{k}"' for k in bo_examples[:5])
            lines.append(
                f"{quoted} are all breakout simultaneously across "
                f"{len(group_clusters)} separate clusters."
            )
        lines.append(
            "People are searching for this from multiple angles — which means "
            "the demand exists whether the product takes one angle or covers all three. "
            "Harder to build than Option A but the signal is unusually strong. "
            "The data will still be here in a month."
        )
        lines.append("")
    elif top:
        bo = _breakout_kws(top)
        lines.append(f"**{top['cluster_name']}** — score {top['cluster_score']}, {top['member_count']} keywords")
        lines.append("")
        if bo:
            lines.append(f"Breakout keywords: {', '.join(chr(34) + k + chr(34) for k in bo[:3])}")
            lines.append("")

    # --- My read ---
    lines.append("---")
    lines.append("")
    lines.append("**My read:**")
    lines.append("")
    if fast and group_clusters:
        lines.append(
            f"Start with Option A — the keyword is specific, the use case is clear, "
            f"and you can ship it before the trend peaks. "
            f"Option B is the better business — multiple clusters all pointing at the same need "
            f"is a rare signal — but it's a longer road. "
            f"Do A first, validate you can rank and convert, then reassess B."
        )
    elif fast:
        lines.append(
            f"Option A is the clear first move. "
            f"The search query is specific enough to rank for with minimal effort, "
            f"and the use case is unambiguous."
        )
    elif group_clusters:
        lines.append(
            f"No obvious fast-build keyword today, but Option B has unusually strong signal. "
            f"Worth deeper research into what specifically people can't find."
        )
    elif top:
        lines.append(
            f"**{top['cluster_name']}** is the strongest cluster. "
            f"Look at the breakout keywords for the sharpest product angle."
        )
    lines.append("")

    return "\n".join(lines)


def _reddit_section(clusters: list[dict]) -> str:
    checked = [c for c in clusters if "reddit" in c]
    if not checked:
        return ""

    lines = ["## Reddit Validation", ""]

    for c in checked:
        r = c["reddit"]
        kw_searched = r.get("keyword", c["top_keyword"])
        pain = r.get("pain_signal", False)
        reliable = r.get("pain_reliable", False)
        total = r.get("total_posts", 0)
        subs = list(r.get("subreddit_hits", {}).keys())[:3]
        sub_str = ", ".join(f"r/{s}" for s in subs) if subs else "none"

        lines.append(f"**{c['cluster_name']}** — searched: \"{kw_searched}\"")

        if total == 0:
            lines.append("→ No Reddit results. Signal unconfirmed.")
        elif pain and reliable:
            lines.append(
                f"→ {total} posts · {sub_str} · "
                f"**Pain signal confirmed** — people are actively expressing frustration."
            )
        elif pain and not reliable:
            lines.append(
                f"→ {total} posts · {sub_str} · "
                f"Pain signal flagged but **results appear off-topic** "
                f"(pain words found in unrelated posts). Treat as inconclusive."
            )
        else:
            lines.append(
                f"→ {total} posts · {sub_str} · "
                f"No pain signal detected (topic discussed but not as a frustration)."
            )

        # Show top relevant post if subreddits look on-topic
        if r.get("top_posts"):
            best = r["top_posts"][0]
            lines.append(
                f"   Top post: \"{best['title']}\" "
                f"[r/{best['subreddit']}] score={best['score']:,}"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def generate_briefing(signals: dict) -> str:
    today = signals.get("date", date.today().isoformat())
    clusters = signals.get("clusters", [])
    unclustered = signals.get("unclustered", [])
    sources = signals.get("sources", [])

    editorial_group = _find_editorial_group(clusters)
    shared = _shared_stems(clusters, editorial_group) if len(editorial_group) >= 2 else []

    source_str = " + ".join(sources) if sources else "unknown"
    total_keywords = sum(c["member_count"] for c in clusters) + len(unclustered)

    parts = [
        f"# Trend Briefing — {today}",
        "",
        f"*Sources: {source_str} · {len(clusters)} clusters "
        f"· {total_keywords} scored keywords*",
        "",
        "---",
        "",
        _cluster_table_section(clusters, unclustered),
        "---",
        "",
        _story_section(clusters, editorial_group, shared),
        "---",
        "",
        _build_section(clusters, unclustered, editorial_group),
    ]

    reddit_section = _reddit_section(clusters)
    if reddit_section:
        parts += ["---", "", reddit_section]

    return "\n".join(parts)


def write_briefing(signals: dict, date_str: str) -> Path:
    BRIEFING_DIR.mkdir(exist_ok=True)
    out_path = BRIEFING_DIR / f"briefing_{date_str}.md"
    content = generate_briefing(signals)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate daily trend briefing")
    parser.add_argument("--date", type=str, default=None,
                        help="Date to generate briefing for (YYYY-MM-DD). Default: today.")
    args = parser.parse_args()

    try:
        signals, date_str = _load_signals(args.date)
    except FileNotFoundError as e:
        print(f"[reporter] {e}")
        return

    out_path = write_briefing(signals, date_str)
    print(f"[reporter] Briefing written -> {out_path}")

    # Also print to terminal so it appears in the daily log
    print("\n" + "=" * 60)
    print(generate_briefing(signals))
    print("=" * 60)


if __name__ == "__main__":
    main()
