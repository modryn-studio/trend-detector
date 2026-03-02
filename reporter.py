"""
reporter.py — daily briefing generator

Reads today's signals JSON and writes a plain-English markdown briefing
to briefings/briefing_YYYY-MM-DD.md.

Uses OpenAI Structured Outputs (gpt-5-mini) for:
  - Cluster renaming: transforms Google's labels into human-need descriptions
  - BUILD/WATCH/SKIP decisions: structured actionable verdicts per cluster

Rule-based sections (no LLM):
  1. Cluster table: what's trending, ranked
  2. Macro-theme detection: are multiple clusters covering the same underlying need?
  3. Reddit validation: is the pain real, or did the search hit noise?

If OPENAI_API_KEY is not set, falls back to rule-based only — briefing always generates.

Usage:
  python reporter.py                    # uses today's signals file
  python reporter.py --date 2026-03-01  # specific date
"""

import argparse
import json
import os
import re
from collections import Counter
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DATA_DIR    = Path(__file__).parent / "data"
BRIEFING_DIR = Path(__file__).parent / "briefings"

# ---------------------------------------------------------------------------
# OpenAI setup — optional, briefing degrades gracefully without it
# ---------------------------------------------------------------------------

_OPENAI_MODEL = "gpt-5-mini"
_openai_client = None

_api_key = os.getenv("OPENAI_API_KEY", "")
if _api_key:
    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=_api_key)
    except ImportError:
        print("[reporter] openai package not installed — LLM features disabled")

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


def _lifecycle_tag(cluster: dict) -> str:
    """Derive EARLY / PEAKING / FADING from members' freshness scores.

    freshness_score mapping (from scorer._freshness_from_series):
      100 = peak in last 7 days, 65 = 8-14d, 35 = 15-21d, 10 = 22+d
    We average across members that have a score (time-series enrichment
    only runs for the top ~15 keywords, so some members won't have one).
    """
    scores = [
        m["_raw"]["freshness_score"]
        for m in cluster.get("members", [])
        if m.get("_raw", {}).get("freshness_score") is not None
    ]
    if not scores:
        return ""
    avg = sum(scores) / len(scores)
    if avg >= 85:
        return " `EARLY`"
    if avg >= 50:
        return " `PEAKING`"
    return " `FADING`"


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


# Use the canonical _stem from cluster.py
from cluster import _stem
from competitor_check import check_competition as _check_competition


def _find_pass1_competition(cluster: dict, competition: dict | None) -> dict:
    """Find pass-1 competition data for a cluster.

    After time-series enrichment, a cluster's top_keyword can shift
    (e.g. 'kaumana caves' replaces 'how to set up trip for least amount
    of pto').  Pass-1 checked the OLD top_keyword, so we search all
    member keywords to find a match.
    """
    if not competition:
        return {}
    # Try top_keyword first (fast path — no enrichment shift)
    top_kw = cluster.get("top_keyword", "")
    comp = competition.get(top_kw)
    if comp:
        return comp
    # Fallback: check all member keywords
    for m in cluster.get("members", []):
        comp = competition.get(m["keyword"])
        if comp:
            return comp
    return {}


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
        name = c.get("display_name", c["cluster_name"])
        original = c.get("original_name")
        tag = _lifecycle_tag(c)
        name_cell = f"{name}{tag} *(was: {original})*" if original else f"{name}{tag}"
        lines.append(
            f"| {i} | {name_cell} | {c['cluster_score']} "
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


def _rename_cluster(cluster: dict) -> str:
    """Use GPT-5 Mini to rename a cluster by the human need it represents.

    Input: member keywords + Google's label.
    Output: 3-6 word human-need description, e.g. "Finding friends as an adult".
    Falls back to original name if LLM unavailable.
    """
    if not _openai_client:
        return cluster["cluster_name"]

    keywords = [m["keyword"] for m in cluster["members"][:10]]
    original = cluster["cluster_name"]

    prompt = (
        f"These trending search keywords were grouped into a cluster "
        f"called \"{original}\":\n\n"
        f"{json.dumps(keywords)}\n\n"
        f"What human need or frustration drives ALL of these searches?\n"
        f"Respond with a short phrase (3-6 words) that names the underlying "
        f"need from the searcher's perspective. Not a category label — "
        f"a human need. Examples: 'Finding friends as an adult', "
        f"'Tracking gold as inflation hedge', 'Planning meals on a budget'."
    )

    try:
        resp = _openai_client.responses.create(
            model=_OPENAI_MODEL,
            input=[{"role": "user", "content": prompt}],
            text={"format": {
                "type": "json_schema",
                "name": "cluster_rename",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "human_need_name": {
                            "type": "string",
                            "description": "3-6 word human-need description"
                        }
                    },
                    "required": ["human_need_name"],
                    "additionalProperties": False,
                },
            }},
        )
        parsed = json.loads(resp.output_text)
        name = parsed.get("human_need_name", original)
        return name if name else original
    except Exception as exc:
        print(f"[reporter] LLM rename failed for '{original}': {exc}")
        return original


def _llm_decision(cluster: dict, competition: dict | None,
                   reddit: dict | None) -> dict | None:
    """Use GPT-5 Mini Structured Outputs for BUILD/WATCH/SKIP verdict.

    Returns dict with: decision, confidence, build_idea, target_slug,
    monetization, reason, risk. Returns None on failure.
    """
    if not _openai_client:
        return None

    keywords = [m["keyword"] for m in cluster["members"][:10]]
    top_kw = cluster.get("top_keyword", keywords[0] if keywords else "")
    score = cluster.get("cluster_score", 0)

    # Build context block
    context_parts = [
        f"Cluster: {cluster['cluster_name']}",
        f"Score: {score}",
        f"Keywords: {json.dumps(keywords)}",
        f"Top keyword: {top_kw}",
    ]

    comp = _find_pass1_competition(cluster, competition)
    if comp:
        context_parts.append(
            f"Competition: {comp.get('verdict', 'UNKNOWN')} "
            f"({comp.get('competitor_count', '?')} existing tools)"
        )
        if comp.get("top_competitors"):
            names = [c["domain"] for c in comp["top_competitors"][:3]]
            context_parts.append(f"Top competitors: {', '.join(names)}")

    if reddit:
        pain = reddit.get("pain_signal", False)
        reliable = reddit.get("pain_reliable", False)
        total = reddit.get("total_posts", 0)
        context_parts.append(
            f"Reddit: {total} posts, pain_signal={pain}, reliable={reliable}"
        )

    context = "\n".join(context_parts)

    prompt = (
        f"You are a solo developer evaluating whether to build a tool.\n\n"
        f"{context}\n\n"
        f"Decide: BUILD (strong signal, clear use case, weak competition), "
        f"WATCH (interesting but unclear execution or medium competition), "
        f"or SKIP (strong competition, unclear need, or low signal).\n\n"
        f"Rules:\n"
        f"- Competition RED + no pain signal → SKIP\n"
        f"- Competition RED + strong pain → WATCH (differentiation possible)\n"
        f"- Competition GREEN + pain signal → BUILD\n"
        f"- Reddit inconclusive → downgrade confidence one level\n"
        f"- Score < 50 → SKIP unless exceptional pain signal\n\n"
        f"CRITICAL SCOPE CONSTRAINT: This developer builds alone in 48 hours maximum.\n"
        f"The build_idea MUST be ONE feature, ONE page, ONE clear user action.\n"
        f"If the idea would need a database, user accounts, or more than 3 API\n"
        f"integrations — scope it down until it doesn't.\n\n"
        f"BUILD FOR THE EMOTIONAL BARRIER, NOT THE INFORMATION GAP.\n"
        f"If Reddit posts express fear, loneliness, overwhelm, or frustration,\n"
        f"the tool should address THAT emotion — not just aggregate links.\n"
        f"Ask: 'What feeling stops someone from acting?' then build for that.\n\n"
        f"GOOD ideas: 'First-timer cheat sheet: what to wear, what to say, what to expect at your first hiking club meetup'\n"
        f"BAD ideas:  'A platform with event scheduling, skill-level filters, and matching'\n\n"
        f"COMPETITION QUERIES: Also output competition_queries \u2014 exactly 3 short,\n"
        f"tool-focused search queries to check if your build idea already exists\n"
        f"as a product. Search for the TOOL you'd build, not the raw trend keyword.\n"
        f"Example: trend='how to set up trip for least amount of pto',\n"
        f"idea='PTO optimizer' \u2192 ['pto optimizer tool', 'maximize pto days\n"
        f"calculator', 'vacation day optimizer app']\n"
    )

    try:
        resp = _openai_client.responses.create(
            model=_OPENAI_MODEL,
            input=[{"role": "user", "content": prompt}],
            text={"format": {
                "type": "json_schema",
                "name": "build_decision",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "decision": {
                            "type": "string",
                            "enum": ["BUILD", "WATCH", "SKIP"],
                        },
                        "confidence": {
                            "type": "string",
                            "enum": ["HIGH", "MED", "LOW"],
                        },
                        "build_idea": {
                            "type": "string",
                            "description": "One-sentence product idea",
                        },
                        "target_slug": {
                            "type": "string",
                            "description": "URL-friendly slug, e.g. 'friend-finder'",
                        },
                        "monetization": {
                            "type": "string",
                            "description": "How this makes money (ads, freemium, affiliate)",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Why this decision (2-3 sentences)",
                        },
                        "risk": {
                            "type": "string",
                            "description": "Primary risk (1 sentence)",
                        },
                        "competition_queries": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "3 short tool-focused search queries to verify if this build idea already exists. Never reuse the raw trend keyword.",
                        },
                    },
                    "required": ["decision", "confidence", "build_idea",
                                 "target_slug", "monetization", "reason", "risk",
                                 "competition_queries"],
                    "additionalProperties": False,
                },
            }},
        )
        return json.loads(resp.output_text)
    except Exception as exc:
        print(f"[reporter] LLM decision failed for '{cluster['cluster_name']}': {exc}")
        return None


def _decision_section(
    clusters: list[dict],
    unclustered: list[dict],
    competition: dict | None,
) -> tuple[str, dict]:
    """BUILD/WATCH/SKIP verdicts for top clusters + unclustered.

    Uses LLM when available, falls back to rule-based heuristics.
    Returns (section_text, refined_competition) where refined_competition
    is a dict of keyword -> competition result from LLM-generated queries.
    """
    lines = ["## Build Decisions", ""]
    refined_competition: dict = {}  # LLM-query-based results

    if not _openai_client:
        lines.append("*OPENAI_API_KEY not set — using rule-based heuristics.*")
        lines.append("")

    # Evaluate top 3 clusters + top 2 unclustered
    targets: list[tuple[str, dict, dict | None]] = []  # (name, data, reddit)
    for c in clusters[:3]:
        targets.append((c["cluster_name"], c, c.get("reddit")))

    for t in unclustered[:2]:
        # Wrap unclustered as a pseudo-cluster for consistent handling
        pseudo = {
            "cluster_name": t["keyword"],
            "cluster_score": t["score"],
            "top_keyword": t["keyword"],
            "members": [t],
        }
        targets.append((t["keyword"], pseudo, None))

    for name, data, reddit in targets:
        top_kw = data.get("top_keyword", name)
        has_pain = reddit and reddit.get("pain_signal", False)

        # RED gate: if Pass 1 competition already says RED and there's no
        # Reddit pain signal, skip the LLM call entirely — obvious SKIP.
        # Saves ~$0.02/cluster now, 60-70 calls/day at Phase 2 scale.
        pass1_data = _find_pass1_competition(data, competition)
        pass1_verdict = pass1_data.get("verdict", "")

        if pass1_verdict == "RED" and not has_pain:
            comp_count = pass1_data.get("competitor_count", 0)
            top_domains = [c["domain"] for c in pass1_data.get(
                "top_competitors", [])[:3]]
            domains_str = ", ".join(top_domains) if top_domains else "various"
            lines.append(f"### 🔴 SKIP — {name} [HIGH]")
            lines.append("")
            lines.append(
                f"**Reasoning:** Pass 1 competition check found "
                f"{comp_count} existing tools ({domains_str}). "
                f"No Reddit pain signal to justify differentiation. "
                f"Skipped LLM evaluation."
            )
            lines.append("")
            print(f"[reporter] RED gate: skipping LLM for '{name}' "
                  f"(pass-1 RED, {comp_count} tools, no pain)")
            continue

        decision = _llm_decision(data, competition, reddit)

        if decision:
            # --- Refined competition check using LLM-generated queries ---
            comp_queries = decision.get("competition_queries", [])
            if comp_queries:
                print(f"[reporter] Refined competition check for '{name}': "
                      f"{comp_queries[:2]}")
                # Use the keyword pass-1 checked (for incumbent matching),
                # not the post-enrichment top_kw which may be unrelated
                pass1_kw = pass1_data.get("keyword", top_kw)
                refined = _check_competition(
                    pass1_kw, search_queries=comp_queries
                )
                # Key by display name so the competition section doesn't
                # show PTO results under 'kaumana caves'
                display_name = data.get("display_name", name)
                refined_key = f"{display_name} (build-idea check)"
                refined["_queries_note"] = comp_queries[:2]
                refined_competition[refined_key] = refined

                # Override BUILD → WATCH if refined check finds heavy competition
                if (decision["decision"] == "BUILD"
                        and refined["verdict"] == "RED"):
                    decision["decision"] = "WATCH"
                    decision["reason"] += (
                        f" [Revised: refined competition search for "
                        f"'{comp_queries[0]}' found "
                        f"{refined['competitor_count']} existing tools — "
                        f"downgraded from BUILD to WATCH.]"
                    )

            icon = {"BUILD": "🟢", "WATCH": "🟡", "SKIP": "🔴"}.get(
                decision["decision"], "❓"
            )
            lines.append(
                f"### {icon} {decision['decision']} — {name} "
                f"[{decision['confidence']}]"
            )
            lines.append("")
            lines.append(f"**Idea:** {decision['build_idea']}")
            lines.append(f"**Slug:** `{decision['target_slug']}`")
            lines.append(f"**Monetization:** {decision['monetization']}")
            lines.append(f"**Reasoning:** {decision['reason']}")
            lines.append(f"**Risk:** {decision['risk']}")
        else:
            # Rule-based fallback
            score = data.get("cluster_score", 0)
            comp_fallback = _find_pass1_competition(data, competition)
            comp_verdict = comp_fallback.get("verdict", "UNKNOWN")

            has_pain = reddit and reddit.get("pain_signal", False)

            if comp_verdict == "RED" and not has_pain:
                verdict = "SKIP"
                icon = "🔴"
            elif comp_verdict == "GREEN" and has_pain:
                verdict = "BUILD"
                icon = "🟢"
            elif score >= 70 and comp_verdict in ("GREEN", "UNKNOWN"):
                verdict = "BUILD"
                icon = "🟢"
            elif score >= 50:
                verdict = "WATCH"
                icon = "🟡"
            else:
                verdict = "SKIP"
                icon = "🔴"

            lines.append(f"### {icon} {verdict} — {name}")
            lines.append("")
            lines.append(
                f"Score: {score} · Competition: {comp_verdict}"
                + (f" · Pain: {'yes' if has_pain else 'no'}"
                   if reddit else " · Reddit: not checked")
            )

        lines.append("")

    return "\n".join(lines), refined_competition


def _competition_section(competition: dict | None) -> str:
    """Render competitor check results."""
    if not competition:
        return ""

    lines = ["## Competition Check", ""]

    for kw, data in competition.items():
        verdict = data.get("verdict", "UNKNOWN")
        icon = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "🔴"}.get(verdict, "❓")
        count = data.get("competitor_count", 0)
        lines.append(f"**{kw}** — {icon} {verdict} ({count} tools found)")

        # Show what was actually searched (refined entries have this)
        queries_note = data.get("_queries_note")
        if queries_note:
            q_str = ", ".join(f'"{q}"' for q in queries_note)
            lines.append(f"  Searched: {q_str}")

        if data.get("top_competitors"):
            for comp in data["top_competitors"][:3]:
                lines.append(f"  - [{comp['domain']}]({comp['url']})")
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

def generate_briefing(signals: dict, competition: dict | None = None) -> str:
    today = signals.get("date", date.today().isoformat())
    clusters = signals.get("clusters", [])
    unclustered = signals.get("unclustered", [])
    sources = signals.get("sources", [])

    editorial_group = _find_editorial_group(clusters)
    shared = _shared_stems(clusters, editorial_group) if len(editorial_group) >= 2 else []

    # Rename clusters using LLM (falls back to original name)
    for c in clusters:
        original = c["cluster_name"]
        renamed = _rename_cluster(c)
        if renamed != original:
            c["display_name"] = renamed
            c["original_name"] = original
        else:
            c["display_name"] = original

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
    ]

    decision_text, refined_competition = _decision_section(
        clusters, unclustered, competition
    )
    parts.append(decision_text)

    # Merge refined (LLM-query-based) competition with keyword-based results.
    # Refined results override keyword-based for the same top_keyword.
    merged_competition = dict(competition) if competition else {}
    merged_competition.update(refined_competition)

    comp_section = _competition_section(merged_competition)
    if comp_section:
        parts += ["---", "", comp_section]

    reddit_section = _reddit_section(clusters)
    if reddit_section:
        parts += ["---", "", reddit_section]

    return "\n".join(parts)


def write_briefing(signals: dict, date_str: str,
                   competition: dict | None = None) -> Path:
    BRIEFING_DIR.mkdir(exist_ok=True)
    out_path = BRIEFING_DIR / f"briefing_{date_str}.md"
    content = generate_briefing(signals, competition=competition)
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

    out_path = write_briefing(signals, date_str, competition=None)
    print(f"[reporter] Briefing written -> {out_path}")

    # Also print to terminal so it appears in the daily log
    print("\n" + "=" * 60)
    print(generate_briefing(signals, competition=None))
    print("=" * 60)


if __name__ == "__main__":
    main()
