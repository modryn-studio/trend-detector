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

import re

# --- Noise filters -------------------------------------------------------

BRAND_NOISE = {
    # AI models & platforms
    "claude", "chatgpt", "gemini", "openai", "copilot",
    "midjourney", "perplexity", "grok", "openclaw",
    "llama", "mistral", "anthropic", "groq", "deepseek",
    "stability", "runway", "sora", "cohere", "ideogram",
    # Dev tools
    "cursor", "replit", "windsurf", "github",
    "notion", "figma", "slack", "zapier",
    # Gaming
    "xbox", "playstation", "nintendo", "steam", "roblox", "fortnite",
    # Finance
    "cash app", "venmo", "paypal", "robinhood", "coinbase",
    # Enterprises / media
    "pennymac", "johnson and johnson", "tesla", "apple",
    "amazon", "google", "microsoft", "meta", "netflix",
    "spacex", "palantir", "nvidia",
    "wall street journal", "cnn", "fox news", "nyt", "bbc",
}

# Compiled once at import. Word boundaries prevent "meta" from matching
# "metadata", "apple" from matching "pineapple", etc.
_BRAND_RE = re.compile(
    r'\b(?:' + '|'.join(re.escape(b) for b in BRAND_NOISE) + r')\b'
)

# Terms too broad or unrelated to have a buildable problem behind them
GENERIC_NOISE = {
    "artificial intelligence", "machine learning", "ai", "technology",
    "health tips", "fitness tips", "health", "fitness", "wellness",
    "productivity", "how to be productive", "personal finance",
    "make money online", "work from home", "5g", "internet",
    "beer", "holi", "oil prices today", "gasbuddy",
}

# News/events/people noise — trending but not buildable
# Note: "college" and "university" omitted — "college budget tracker",
# "university course planner" etc. are buildable. "school" kept because
# it mainly surfaces in "school delays/closings" news events.
NEWS_NOISE_WORDS = [
    "shooting", "killed", "died", "death", "arrested", "trial",
    "crash", "fire", "earthquake", "hurricane", "flood", "tornado",
    "election", "vote", "president", "congress", "senate",
    "war", "attack", "bomb", "explosion", "hostage",
    "school",
]

# Sports noise — huge volume, zero build signal
# Note: "coach" omitted — "life coach", "career coach", "sales coach" are buildable.
SPORTS_NOISE_WORDS = [
    "vs", "score", "game", "match", "nfl", "nba", "nhl", "mlb",
    "fifa", "ufc", "boxing", "playoff", "championship", "tournament",
    "league", "roster", "draft",
    "basketball", "football", "soccer", "baseball", "hockey",
    "ncaa", "uconn", "march madness",
]

# Entertainment noise
ENTERTAINMENT_NOISE_WORDS = [
    "movie", "show", "episode", "trailer", "season", "premiere",
    "concert", "album", "song", "actress", "actor",
]


# Common first names that appear in trending people topics.
# Used to detect "First Last" person names without false-positives on
# compound nouns like "stock futures" or "interest rates".
PERSON_FIRST_NAMES = {
    "jeff", "mike", "michael", "john", "jane", "james", "joe", "joseph",
    "bob", "bill", "william", "sam", "samuel", "tom", "thomas", "dan", "daniel",
    "ben", "benjamin", "chris", "christopher", "mark", "paul", "peter",
    "steve", "steven", "stephen", "ryan", "kevin", "scott", "eric",
    "alex", "alexander", "matt", "matthew", "jason", "adam", "brian",
    "kyle", "brad", "dave", "david", "rob", "robert", "tim", "timothy",
    "jake", "jacob", "josh", "joshua", "sean", "drew", "derek", "aaron",
    "justin", "travis", "tyler", "zach", "zachary", "wade", "rick", "richard",
    "ken", "kenneth", "neil", "carl", "pat", "patrick", "ed", "edward", "jim",
    "gary", "larry", "donald", "elon", "lebron", "kobe", "shaq",
    "trump", "biden", "barack", "bernie", "kamala", "hillary", "nancy",
    "tony", "anthony", "nick", "nicholas", "andrew", "ray", "russell",
    "ty", "chad", "greg", "gregory", "keith", "roger", "phil", "phillip",
    "doug", "douglas", "terry", "jerry", "randy", "johnny", "bobby",
    "jimmy", "tommy", "danny", "freddy", "charlie", "frank", "hank",
    # Female first names
    "amy", "sarah", "jennifer", "jessica", "ashley", "emily", "amanda",
    "lisa", "nicole", "karen", "rachel", "michelle", "laura", "megan",
    "taylor", "hannah", "brittany", "samantha", "stephanie", "heather",
    "viola", "oprah", "beyonce", "rihanna", "serena", "venus",
    "ivanka", "melania", "meghan",
    "noah", "ted", "ausar", "vj", "liam", "emma", "olivia", "ava",
    "sophia", "isabella", "mia", "charlotte", "amelia", "harper",
    "ethan", "mason", "logan", "lucas", "owen", "elijah", "aiden",
}


def is_buildable(keyword: str) -> bool:
    """Filter out noise. Returns True if this keyword might represent
    a buildable opportunity worth scoring."""
    kw = keyword.lower()

    # Brand names — word-boundary match prevents "meta" hitting "metadata",
    # "apple" hitting "pineapple", etc.
    if _BRAND_RE.search(kw):
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

    # Too short = not a searchable keyword
    if len(kw) <= 3:
        return False

    # Too long = headline, not a keyword
    if len(kw) > 60:
        return False

    # Person names — "First Last" format. Check if first word is a known
    # first name so we don't catch compound nouns like "stock futures".
    words = kw.split()
    if len(words) == 2 and all(w.isalpha() for w in words) and words[0] in PERSON_FIRST_NAMES:
        return False

    # Single-word all-alpha with no action/tool intent = likely a name or
    # brand we didn't list. Buildable queries almost always have context:
    # "bitcoin atm", "friend app", "how to X". A bare "allmendinger" is noise.
    if len(words) == 1 and kw.isalpha() and kw not in GENERIC_NOISE:
        # Allow if it contains a buildable signal word as substring
        if not any(s in kw for s in ["app", "tool", "bot", "tracker", "finder"]):
            return False

    return True


# --- Buildability heuristic -----------------------------------------------

HIGH_BUILDABILITY = [
    # Explicit tool shapes
    "tool", "app", "tracker", "generator", "checker", "calculator",
    "finder", "manager", "planner", "dashboard", "monitor", "assistant",
    "bot", "extension", "plugin", "automation", "converter", "analyzer",
    "summarizer", "scheduler", "writer", "builder", "scanner",
    # Tool-adjacent — signals a specific need even without "app" or "tool"
    "atm", "locator", "near me", "fee", "fees", "map", "lookup",
    "compare", "comparison", "rates", "price", "cost", "how to",
    "alternative", "review", "best",
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
    """Map Google's volume estimate onto 0–100.
    volume=0 means unknown (e.g. email source) — use neutral 50 so
    we don't penalize or reward missing data."""
    if volume == 0:
        return 50.0, "unknown"
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
        "source":       trend.get("source", "trendspy"),
        "source_count": trend.get("source_count", 1),
        "_raw": {
            "growth_score":       growth,
            "volume_score":       vol_score,
            "buildability_score": build_score,
            "freshness_score":    freshness,
            "google_volume":      trend["volume"],
            "google_growth_pct":  trend["growth_pct"],
        },
    }
