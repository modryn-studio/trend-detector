"""
competitor_check.py — check if tools already exist for a trend keyword

Uses Brave Search API to check for existing tools on product-discovery
domains. Determines GREEN/YELLOW/RED signal.

Note: Google Custom Search JSON API is closed to new customers (Feb 2026).
Brave Search API is the drop-in replacement:
  - $5 free credits/month = 1,000 free queries/month
  - Pipeline uses ~5 queries/run (~150/month) — within free tier

Setup:
  1. Sign up at https://api-dashboard.search.brave.com/register
  2. Create an API key (free plan — $5 credit/month auto-applied)
  3. Add to .env:
       BRAVE_SEARCH_KEY=your-api-key

Results are filtered client-side to only count hits on tool-discovery
domains (ProductHunt, GitHub, G2, Capterra, AlternativeTo, etc.) so the
GREEN/YELLOW/RED signal remains precise regardless of full-web results.
"""

import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

_BRAVE_KEY = os.getenv("BRAVE_SEARCH_KEY", "")
_REQUEST_DELAY = 1.2  # Brave free tier: 1 req/sec

# Domains that are unambiguous evidence of an existing purpose-built tool.
# Only results from these domains count toward competitor score.
_TOOL_DOMAINS = {
    "producthunt.com", "alternativeto.net", "github.com",
    "g2.com", "capterra.com", "appsumo.com", "getapp.com",
    "sourceforge.net", "softwareadvice.com", "toolify.ai",
}

# Title-only signals that indicate a purpose-built tool on unknown domains.
# Checked against the page TITLE only — not the snippet, because generic
# words like "find" or "track" appear in every blog post description.
# These are words that a tool/product puts in its own page title.
_TITLE_TOOL_SIGNALS = [
    "tracker", "tracking", "monitor", "calculator", "generator",
    "builder", "planner", "finder", "dashboard", "countdown",
    "app", "free trial", "pricing", "sign up", "get started",
    "download the", "schedule", "live chart", "live data",
]

# SaaS-heavy TLDs — a title signal + one of these domains is very likely a tool
_TOOL_TLDS = {".io", ".app", ".tools", ".dev", ".software"}

# Well-known incumbents per topic.  If any result URL contains one of these
# domains, it counts as a tool hit regardless of snippet text.  Only add
# domains that ARE a tool/product — not news or encyclopedias.
_KNOWN_INCUMBENTS: dict[str, set[str]] = {
    # space / launch
    "spacex": {"rocketlaunch.live", "nextspaceflight.com", "spacex.com",
               "spaceflightnow.com", "everydayastronaut.com"},
    "launch": {"rocketlaunch.live", "nextspaceflight.com"},
    # oil / commodities
    "oil": {"oilprice.com", "tradingeconomics.com", "investing.com",
            "marketwatch.com", "bloomberg.com"},
    "crude": {"oilprice.com", "tradingeconomics.com", "investing.com"},
    "commodity": {"tradingeconomics.com", "investing.com"},
    # stock / finance
    "stock": {"tradingview.com", "finance.yahoo.com", "marketwatch.com",
              "investing.com", "seekingalpha.com"},
    # social / meetup
    "club": {"meetup.com", "eventbrite.com"},
    "meetup": {"meetup.com"},
    "friends": {"bumble.com", "meetup.com"},
    # travel
    "flight": {"google.com/travel", "kayak.com", "skyscanner.com",
               "expedia.com", "hopper.com"},
    "hotel": {"booking.com", "hotels.com", "expedia.com", "trivago.com"},
    "pto": set(),  # nothing purpose-built yet
}

# Domains that are always informational — never count them as tools even
# if snippet text matches.  Keeps false positives out.
_INFORMATIONAL_DOMAINS = {
    "wikipedia.org", "reddit.com", "quora.com", "stackoverflow.com",
    "medium.com", "youtube.com", "twitter.com", "x.com",
    "nytimes.com", "bbc.com", "cnn.com", "reuters.com",
    "apnews.com", "theguardian.com", "news.google.com",
}

# Query suffixes that reveal tool-intent competition
_TOOL_SUFFIXES = ["tool", "calculator", "finder", "app", "generator"]


def _is_tool_result(item: dict, keyword: str = "") -> bool:
    """Return True if a result looks like an existing purpose-built tool.

    Three-layer check:
    1. Known tool-discovery domains (ProductHunt, GitHub, G2…)
    2. Known incumbent domains for the keyword's topic
    3. Functional-language signals in the snippet/title on non-informational
       domains (catches tools that don't live on product-listing sites)
    """
    url = item.get("url", "").lower()
    title = item.get("title", "").lower()
    snippet = item.get("description", "").lower()

    # Skip known informational sites — never tools
    for domain in _INFORMATIONAL_DOMAINS:
        if domain in url:
            return False

    # Layer 1: product-discovery domains
    for domain in _TOOL_DOMAINS:
        if domain in url:
            return True

    # Layer 2: known incumbents for this keyword's topic
    kw_lower = keyword.lower()
    for trigger, domains in _KNOWN_INCUMBENTS.items():
        if trigger in kw_lower:
            for domain in domains:
                if domain in url:
                    return True

    # Layer 3: functional language in title (not snippet — too many false positives
    # from blog posts that mention "track" or "find" incidentally)
    for signal in _TITLE_TOOL_SIGNALS:
        if signal in title:
            return True

    return False


def _search_brave(query: str, count: int = 10) -> list[dict]:
    """Run a Brave web search query. Returns normalized result items."""
    if not _BRAVE_KEY:
        return []

    encoded_q = urllib.request.quote(query, safe='')
    url = (
        f"https://api.search.brave.com/res/v1/web/search"
        f"?q={encoded_q}&count={count}&search_lang=en"
    )

    try:
        req = urllib.request.Request(
            url,
            headers={"X-Subscription-Token": _BRAVE_KEY, "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        print(f"[competitor] Brave search failed for '{query}': {e}")
        return []

    # Normalize — keep description/snippet for functional-signal matching
    return [
        {
            "url": r.get("url", ""),
            "title": r.get("title", ""),
            "description": r.get("description", ""),
        }
        for r in data.get("web", {}).get("results", [])
    ]


def check_competition(keyword: str, search_queries: list[str] | None = None) -> dict:
    """
    Check if purpose-built tools already exist for a keyword.

    Searches Brave for tool-intent queries, then filters results to only
    count hits on known tool-discovery domains (ProductHunt, GitHub, etc.).

    Args:
        keyword: The keyword or topic to check.
        search_queries: Optional LLM-generated queries to search instead of
            building default suffix-based queries. Use this when the LLM has
            proposed a specific build idea that differs from the raw keyword.

    Returns:
    {
        "keyword": "bitcoin atm",
        "queries_searched": ["bitcoin atm tool", "bitcoin atm finder", ...],
        "competitor_count": 3,
        "top_competitors": [{"title": "...", "url": "...", "domain": "..."}],
        "verdict": "GREEN" | "YELLOW" | "RED",
    }
    """
    if not _BRAVE_KEY:
        return {
            "keyword": keyword,
            "queries_searched": [],
            "competitor_count": 0,
            "top_competitors": [],
            "verdict": "UNKNOWN",
            "error": "BRAVE_SEARCH_KEY not configured",
        }

    if search_queries:
        # LLM-generated queries — use directly, cap at 2 to conserve quota
        queries = search_queries[:2]
    else:
        # Build queries: "keyword tool", "keyword finder", etc.
        # Only search 2 most relevant suffixes to conserve API quota
        kw_lower = keyword.lower()
        best_suffixes = []
        for s in _TOOL_SUFFIXES:
            if s not in kw_lower:
                best_suffixes.append(s)
            if len(best_suffixes) >= 2:
                break
        queries = [f"{keyword} {s}" for s in best_suffixes]

    all_tools: list[dict] = []
    seen_domains: set[str] = set()
    total_results = 0  # raw results across all queries; low count = Brave index gap

    for query in queries:
        time.sleep(_REQUEST_DELAY)
        results = _search_brave(query, count=10)
        total_results += len(results)
        for item in results:
            if _is_tool_result(item, keyword=keyword):
                url = item.get("url", "")
                # Extract domain (e.g. producthunt.com) as dedup key
                domain = url.split("/")[2] if url.startswith("http") else url
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    all_tools.append({
                        "title":  item.get("title", ""),
                        "url":    url,
                        "domain": domain,
                    })

    count = len(all_tools)

    # Brave's index is smaller than Google's — a near-empty result set means
    # the topic is too niche/new to read, not that no tools exist.
    if total_results < 3:
        verdict = "INCONCLUSIVE"
    elif count <= 1:
        verdict = "GREEN"
    elif count <= 3:
        verdict = "YELLOW"
    else:
        verdict = "RED"

    return {
        "keyword":          keyword,
        "queries_searched":  queries,
        "total_results":     total_results,
        "competitor_count":  count,
        "top_competitors":   all_tools[:5],
        "verdict":           verdict,
    }


def validate_build_opportunities(clusters: list[dict],
                                 unclustered: list[dict],
                                 max_checks: int = 5) -> dict:
    """
    Run competition checks for top build-worthy keywords.

    Returns dict mapping keyword -> competition result.
    """
    keywords_to_check: list[str] = []

    # Top keyword from each cluster (up to 3)
    for c in clusters[:3]:
        kw = c.get("top_keyword", "")
        if kw and kw not in keywords_to_check:
            keywords_to_check.append(kw)

    # Top unclustered (up to 2)
    for t in unclustered[:2]:
        kw = t.get("keyword", "")
        if kw and kw not in keywords_to_check:
            keywords_to_check.append(kw)

    keywords_to_check = keywords_to_check[:max_checks]

    results = {}
    for kw in keywords_to_check:
        print(f"[competitor] Checking: {kw}")
        result = check_competition(kw)
        results[kw] = result
        icon = {"GREEN": "✅", "YELLOW": "⚠️", "RED": "🔴"}.get(
            result["verdict"], "❓"
        )
        print(f"[competitor]   {icon} {result['verdict']} — "
              f"{result['competitor_count']} tools found")

    return results


# --- Standalone test ---
if __name__ == "__main__":
    import sys
    keyword = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "bitcoin atm"
    print(f"Checking competition for '{keyword}'...\n")
    result = check_competition(keyword)
    print(f"Verdict: {result['verdict']}")
    print(f"Tool count: {result['competitor_count']}")
    print(f"Queries: {result['queries_searched']}")
    if result.get("top_competitors"):
        print(f"\nTop competitors:")
        for c in result["top_competitors"]:
            print(f"  {c['domain']}: {c['title']}")
            print(f"    {c['url']}")
