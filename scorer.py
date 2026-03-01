"""
scorer.py — scoring + filtering

Takes raw trending data from fetcher.py, filters out noise (brands,
sports, news events, generic terms), then scores what's left 0–100.

Two scoring paths:
  1. Quick score — from trending_now metadata alone (volume + growth).
     Used for all trends. No additional API calls.
  2. Full score — adds time-series velocity + freshness when available.
     Used for trends that get a time series from interest_over_time.
"""

# --- Noise filters -------------------------------------------------------

BRAND_NOISE = {
    "claude", "chatgpt", "gemini", "openai", "copilot",
    "midjourney", "perplexity", "grok", "openclaw",
    "notion", "figma", "github", "slack", "zapier",
    "xbox", "playstation", "nintendo", "steam",
    "cash app", "venmo", "paypal", "robinhood", "coinbase",
    "pennymac", "johnson and johnson", "tesla", "apple",
    "amazon", "google", "microsoft", "meta", "netflix",
}

# Terms too broad or unrelated to have a buildable problem behind them
GENERIC_NOISE = {
    "artificial intelligence", "machine learning", "ai", "technology",
    "health tips", "fitness tips", "health", "fitness", "wellness",
    "productivity", "how to be productive", "personal finance",
    "make money online", "work from home", "5g", "internet",
    "beer", "holi", "oil prices today", "gasbuddy",
}

# News/events/people noise — trending but not buildable
NEWS_NOISE_WORDS = [
    "shooting", "killed", "died", "death", "arrested", "trial",
    "crash", "fire", "earthquake", "hurricane", "flood", "tornado",
    "election", "vote", "president", "congress", "senate",
    "war", "attack", "bomb", "explosion", "hostage",
    "university", "college", "school",
]

# Sports noise — huge volume, zero build signal
SPORTS_NOISE_WORDS = [
    "vs", "score", "game", "match", "nfl", "nba", "nhl", "mlb",
    "fifa", "ufc", "boxing", "playoff", "championship", "tournament",
    "league", "roster", "draft", "trade", "coach",
]

# Entertainment noise
ENTERTAINMENT_NOISE_WORDS = [
    "movie", "show", "episode", "trailer", "season", "premiere",
    "concert", "album", "song", "actress", "actor",
]


def is_buildable(keyword: str) -> bool:
    """Filter out noise. Returns True if this keyword might represent
    a buildable opportunity worth scoring."""
    kw = keyword.lower()

    # Brand names
    if any(brand in kw for brand in BRAND_NOISE):
        return False

    # Exact generic matches
    if kw in GENERIC_NOISE:
        return False

    # News/events
    if any(w in kw for w in NEWS_NOISE_WORDS):
        return False

    # Sports
    if any(w in kw for w in SPORTS_NOISE_WORDS):
        return False

    # Entertainment
    if any(w in kw for w in ENTERTAINMENT_NOISE_WORDS):
        return False

    # Too long = headline, not a keyword
    if len(kw) > 60:
        return False

    # Person names (2 words, both alpha) — nearly always news/celebrity noise.
    # Tool-shaped queries are rarely just "firstname lastname".
    words = kw.split()
    if len(words) == 2 and all(w.isalpha() for w in words):
        # Allow if it contains a buildability signal word
        if not any(s in kw for s in HIGH_BUILDABILITY):
            return False

    return True


# --- Buildability heuristic -----------------------------------------------

HIGH_BUILDABILITY = [
    "tool", "app", "tracker", "generator", "checker", "calculator",
    "finder", "manager", "planner", "dashboard", "monitor", "assistant",
    "bot", "extension", "plugin", "automation", "converter", "analyzer",
    "summarizer", "scheduler", "writer", "builder", "scanner",
]

LOW_BUILDABILITY = [
    "stock", "invest", "market", "fund", "insurance", "regulation",
    "policy", "research", "enterprise", "infrastructure", "hardware",
]


def _buildability(keyword: str) -> tuple[float, str]:
    kw = keyword.lower()
    if any(s in kw for s in LOW_BUILDABILITY):
        return 20.0, "low"
    if any(s in kw for s in HIGH_BUILDABILITY):
        return 80.0, "high"
    return 50.0, "medium"


# --- Scoring ---------------------------------------------------------------

# Weights for the composite score. Must sum to 1.0.
# When time series is available, all four are used.
# When it's not, velocity gets redistributed to growth_pct.
WEIGHTS = {
    "growth":       0.35,   # Google's own growth % — primary signal
    "volume":       0.20,   # Absolute search volume
    "buildability": 0.25,   # Can you ship something in 48h?
    "freshness":    0.20,   # Is the trend still rising or already peaked?
}


def _growth_score(growth_pct: float) -> float:
    """Map Google's growth_pct (0–5000+) onto 0–100."""
    # 100% growth → 50, 500% → 83, 1000%+ → ~100
    clamped = min(growth_pct, 1500)
    return round((clamped / 1500) * 100, 1)


def _volume_score(volume: int) -> tuple[float, str]:
    """Map Google's volume estimate onto 0–100."""
    if volume >= 500_000:
        return 100.0, "high"
    elif volume >= 100_000:
        return 75.0, "high"
    elif volume >= 50_000:
        return 60.0, "medium"
    elif volume >= 10_000:
        return 40.0, "medium"
    elif volume >= 1_000:
        return 20.0, "low"
    else:
        return 5.0, "low"


def _freshness_from_series(series: list[float]) -> float:
    """100 if peak is in last 7 days, decays to 10 for 3+ weeks ago."""
    if not series:
        return 50.0
    peak_idx = series.index(max(series))
    days_since = len(series) - 1 - peak_idx
    if days_since <= 7:
        return 100.0
    elif days_since <= 14:
        return 65.0
    elif days_since <= 21:
        return 35.0
    return 10.0


def score_trend(trend: dict, series: list[float] | None = None) -> dict:
    """
    Score a single trend. Returns the canonical output record.

    trend keys: keyword, category, volume, growth_pct, trend_keywords
    series: optional interest_over_time data for richer scoring
    """
    growth  = _growth_score(trend["growth_pct"])
    vol_score, vol_label = _volume_score(trend["volume"])
    build_score, build_label = _buildability(trend["keyword"])

    if series and len(series) >= 7:
        freshness = _freshness_from_series(series)
    else:
        # No time series — assume it's fresh since it's currently trending
        freshness = 85.0

    composite = (
        WEIGHTS["growth"]       * growth      +
        WEIGHTS["volume"]       * vol_score   +
        WEIGHTS["buildability"] * build_score +
        WEIGHTS["freshness"]    * freshness
    )

    # Velocity label from growth_pct
    if trend["growth_pct"] >= 200:
        vel_label = "rising"
    elif trend["growth_pct"] >= 50:
        vel_label = "steady"
    else:
        vel_label = "declining"

    return {
        "keyword":      trend["keyword"],
        "score":        round(composite),
        "velocity":     vel_label,
        "volume":       vol_label,
        "buildability": build_label,
        "category":     trend["category"],
        "_raw": {
            "growth_score":       growth,
            "volume_score":       vol_score,
            "buildability_score": build_score,
            "freshness_score":    freshness,
            "google_volume":      trend["volume"],
            "google_growth_pct":  trend["growth_pct"],
        },
    }
