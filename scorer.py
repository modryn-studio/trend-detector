"""
scorer.py — scoring logic

Scores a raw trend dict (from fetcher.py) 0–100 based on four signals:
  velocity     — week-over-week rise delta
  volume       — absolute search interest
  buildability — can a solo dev ship something in 48h? (heuristic)
  freshness    — has this trend already peaked?

WEIGHTS are the first thing to tune after seeing real output.
The _raw sub-scores in each result make it easy to see which signal
is driving or dragging a trend's composite score.
"""

from typing import Literal

# --- Brand noise (product names, not buildable opportunities) --------
BRAND_NOISE = {
    "claude", "chatgpt", "gemini", "openai", "copilot", 
    "midjourney", "perplexity", "grok", "openclaw",
    "notion", "figma", "github", "slack", "zapier",
}

# --- Generic noise (too broad to build on) ----------------------------
# Terms with high search volume but zero specificity — no problem statement,
# no audience, nothing to ship. Expand as you observe more noise in output.
GENERIC_NOISE = {
    "artificial intelligence", "machine learning", "ai", "technology",
    "health tips", "fitness tips", "health", "fitness", "wellness",
    "productivity", "how to be productive", "personal finance",
    "make money online", "work from home",
}
# Keywords that suggest a concrete, tool-shaped problem a dev can ship in 48h.
# Update these as you observe which trends produce useful tools vs dead ends.

HIGH_BUILDABILITY_SIGNALS = [
    "tool", "app", "tracker", "generator", "checker", "calculator",
    "finder", "manager", "planner", "dashboard", "monitor", "assistant",
    "bot", "extension", "plugin", "automation", "converter", "analyzer",
    "summarizer", "scheduler", "writer", "builder", "scanner",
]

LOW_BUILDABILITY_SIGNALS = [
    "stock", "invest", "market", "fund", "insurance", "regulation",
    "policy", "research", "enterprise", "infrastructure", "hardware",
]

# --- Weights ----------------------------------------------------------------
# Must sum to 1.0. Velocity-heavy because you want trends early, not at peak.
# Tune these after a week of real output.
WEIGHTS = {
    "velocity":     0.40,
    "volume":       0.20,
    "buildability": 0.25,
    "freshness":    0.15,
}

# Type aliases for the output labels
Velocity    = Literal["rising", "steady", "declining"]
Volume      = Literal["high", "medium", "low"]
Buildability = Literal["high", "medium", "low"]


def _velocity_score(series: list[float]) -> tuple[float, Velocity]:
    """
    Compare the last 7 days avg to the prior 7 days avg.
    Maps the percentage delta onto a 0–100 scale centered at 50 (no change).
    """
    if len(series) < 14:
        return 50.0, "steady"

    recent = sum(series[-7:])  / 7
    prior  = sum(series[-14:-7]) / 7

    if prior == 0:
        # Trend appeared from nothing — treat as maximum velocity
        delta_pct = 200.0 if recent > 0 else 0.0
    else:
        delta_pct = ((recent - prior) / prior) * 100

    # Clamp to [-100, 200] then normalize to [0, 100]
    clamped    = max(-100.0, min(200.0, delta_pct))
    normalized = (clamped + 100) / 3  # -100 → 0.0, 50 → 50.0, 200 → 100.0

    if delta_pct > 20:
        label: Velocity = "rising"
    elif delta_pct < -20:
        label = "declining"
    else:
        label = "steady"

    return round(normalized, 1), label


def _volume_score(series: list[float]) -> tuple[float, Volume]:
    """
    Google Trends already scales interest 0–100 relative to peak in window,
    so we use the peak value directly as the volume score.
    """
    if not series:
        return 0.0, "low"

    peak = max(series)

    if peak >= 60:
        label: Volume = "high"
    elif peak >= 30:
        label = "medium"
    else:
        label = "low"

    return round(peak, 1), label


def _buildability_score(keyword: str) -> tuple[float, Buildability]:
    """
    Heuristic: does this keyword look like something shippable in 48h?
    Low-signal words (e.g. 'regulation') score low. Tool-shaped words score high.
    Defaults to medium when neither list matches — most trends land here.
    """
    kw_lower = keyword.lower()

    if any(sig in kw_lower for sig in LOW_BUILDABILITY_SIGNALS):
        return 20.0, "low"

    if any(sig in kw_lower for sig in HIGH_BUILDABILITY_SIGNALS):
        return 80.0, "high"

    return 50.0, "medium"


def _freshness_score(series: list[float]) -> float:
    """
    Penalize trends that peaked weeks ago — you'd be late.
    100 if peak is in the most recent 7 days, decays to 10 if it was 3+ weeks ago.
    """
    if not series:
        return 50.0

    peak_idx        = series.index(max(series))
    days_since_peak = len(series) - 1 - peak_idx

    if days_since_peak <= 7:
        return 100.0
    elif days_since_peak <= 14:
        return 65.0
    elif days_since_peak <= 21:
        return 35.0
    else:
        return 10.0


def score_trend(trend: dict) -> dict | None:
    """
    Score a single raw trend dict from fetcher.py.
    Returns None if it's brand noise, below interest floor, or not buildable.
    Returns the canonical output record (matching the schema in context.md).
    """
    kw_lower = trend["keyword"].lower()
    
    # Skip known product brands — they're not buildable opportunities
    if any(brand in kw_lower for brand in BRAND_NOISE):
        return None

    # Skip generic terms — too broad to have a problem statement worth building on
    if kw_lower in GENERIC_NOISE:
        return None
    
    series = trend["interest_series"]

    # Skip low-interest keywords — they're noise, not trends worth building on.
    # Floor is intentionally conservative; raise it if output is still spammy.
    RECENT_INTEREST_FLOOR = 15
    recent_avg = sum(series[-7:]) / max(len(series[-7:]), 1)
    if recent_avg < RECENT_INTEREST_FLOOR:
        return None

    vel_score,   vel_label   = _velocity_score(series)
    vol_score,   vol_label   = _volume_score(series)
    build_score, build_label = _buildability_score(trend["keyword"])
    fresh_score              = _freshness_score(series)

    composite = (
        WEIGHTS["velocity"]     * vel_score   +
        WEIGHTS["volume"]       * vol_score   +
        WEIGHTS["buildability"] * build_score +
        WEIGHTS["freshness"]    * fresh_score
    )

    return {
        "keyword":      trend["keyword"],
        "score":        round(composite),
        "velocity":     vel_label,
        "volume":       vol_label,
        "buildability": build_label,
        "category":     trend["category"],
        # Sub-scores make it easy to see what's driving each result.
        # Strip _raw from the output once weights are tuned.
        "_raw": {
            "velocity_score":     vel_score,
            "volume_score":       vol_score,
            "buildability_score": build_score,
            "freshness_score":    fresh_score,
        },
    }
