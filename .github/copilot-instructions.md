# Trend Detector — Copilot Context

## What This Is
A private Python pipeline that runs daily, pulls rising search trends, scores them, and writes a JSON file Luke reads every morning to decide what to build next. No web server. No database. No users. Just a script and flat files.

## Phase 1 (this repo) — Private Pipeline
- One script: `pipeline.py`
- Runs on a cron job at 6:00 AM daily
- Output: `data/trends_YYYY-MM-DD.json`
- Keep ALL output files — the history becomes the Phase 2 demo

## Phase 2 (future, separate repo) — Public Tool
When Google Trends API alpha access arrives, this becomes a public web tool built on modryn-studio's Next.js boilerplate. Don't build Phase 2 infrastructure here.

## Stack
- Python 3.12+
- **pytrends-modern** (`pip install pytrends-modern`) — NOT the original pytrends (archived April 2025, no longer maintained). pytrends-modern is a drop-in replacement with built-in rate limit management, RSS support, and active maintenance.
- System cron or `schedule` library
- Flat JSON files in `/data` — no database

## Project Structure
```
pipeline.py          ← entry point, run this
discover.py          ← Stage 1: fetch trending via RSS (fast, no API quota used)
filter.py            ← Stage 2: strip noise (sports, celebs, news events)
scorer.py            ← Stage 3: score filtered trends via interest_over_time
output.py            ← Stage 4: write data/trends_YYYY-MM-DD.json
data/
  trends_YYYY-MM-DD.json   ← daily output, NEVER delete these
requirements.txt
.gitignore           ← gitignore .env but NOT /data — keep all history
```

## Output Format
```json
{
  "date": "2026-02-26",
  "trends": [
    {
      "term": "...",
      "score": 87.0,
      "velocity": 42.0,
      "recent_interest": 68.0
    }
  ]
}
```

## Stage 1 — Discover (RSS first)
Use the RSS method as primary — it's 0.2s, uses no API quota, returns 10 live trending searches:
```python
from pytrends_modern import TrendsRSS
rss = TrendsRSS()
trends = rss.get_trends(geo='US')
```
Fall back to `trending_searches` only if RSS fails.

## Stage 2 — Filter
Strip noise keywords (sports, news events, entertainment). Simple keyword blacklist for v1.
```python
NOISE = ["nfl","nba","nhl","mlb","vs","score","game","match",
         "died","death","arrested","trial","movie","show","episode"]
def is_buildable(term: str) -> bool:
    t = term.lower()
    return not any(n in t for n in NOISE)
```

## Stage 3 — Score (IMPORTANT — read carefully)

**Batch keywords — 5 per API call, never 1.** One call per keyword = 20 calls for 20 trends = guaranteed rate limit. Batch into groups of 5.

**Minimum interest floor of 15.** Velocity of +40 with recent_interest of 3 means the trend is rising from nothing — no traffic opportunity. Skip it.

**Drop related queries from v1.** That's a separate API call per keyword for only 20% of the score. Not worth doubling requests. Add in v2.

```python
import time

def score_trends(terms: list[str]) -> list[dict]:
    results = []
    # Batch into groups of 5 — pytrends API max per call
    chunks = [terms[i:i+5] for i in range(0, len(terms), 5)]
    for chunk in chunks:
        pytrends.build_payload(chunk, timeframe='today 3-m')
        df = pytrends.interest_over_time()
        time.sleep(5)  # always sleep between API calls

        for term in chunk:
            if term not in df.columns:
                continue
            recent   = df[term].tail(4).mean()   # last 4 weeks
            older    = df[term].head(4).mean()   # first 4 weeks
            velocity = recent - older

            # Skip trends rising from nothing — no traffic value
            if recent < 15:
                continue

            results.append({
                "term": term,
                "velocity": round(velocity, 1),
                "recent_interest": round(recent, 1),
                "score": round((velocity * 0.6) + (recent * 0.4), 1),
            })
    return sorted(results, key=lambda x: x["score"], reverse=True)
```

**Scoring weights (v1):**
| Signal | Weight | Rationale |
|--------|--------|-----------|
| Velocity (recent - older) | 60% | Primary signal — rising = opportunity window |
| Recent interest | 40% | Floor 15 required — no traffic = skip |
| Related queries | dropped | Add in v2 — not worth the extra API calls |

## Rate Limit Defense
Build this wrapper around all API calls:
```python
def safe_request(fn, *args, sleep=5, **kwargs):
    try:
        result = fn(*args, **kwargs)
        time.sleep(sleep)
        return result
    except Exception as e:
        if "429" in str(e):
            print("Rate limited — sleeping 60s")
            time.sleep(60)
            return fn(*args, **kwargs)  # one retry
        raise e
```

## Code Style
- Write as a senior engineer: minimal surface area, obvious naming
- Comments explain WHY, not what
- One file = one responsibility
- Early returns for error handling
- Never add complexity before Phase 2 requires it

## Seed Design — Informational vs Tool-Shaped Queries

This is the most important tuning lever in the pipeline. The seeds control what kinds of rising queries surface, and not all rising queries are equal.

**Informational queries** — high volume, no product behind them:
- `what is a task manager`, `how to use signal app`, `best productivity planners`
- These are orientation queries. The person is still learning, not frustrated.
- A rising informational query means a topic is getting popular — it does NOT mean there's a gap to build into.

**Tool-shaped queries** — specific friction, rising, buildable:
- `too many browser tabs`, `can't keep track of tasks`, `waterproof fitness tracker`
- These are complaint or solution-seeking queries. The person has a specific problem.
- A rising tool-shaped query means people are actively looking for something that might not exist yet.

**The rule:** if a rising query sounds like something you'd type when annoyed, it's a build signal. If it sounds like something you'd type in a homework assignment, it's noise.

**How to enforce this in seeds:** phrase seeds as specific frictions, not category names.
- Bad: `productivity app`, `task manager` → surfaces "what is X", "how to use X"
- Good: `too many browser tabs`, `overwhelmed at work` → surfaces complaint-adjacent queries

**What to do when output is mostly informational:** tighten 3–4 seeds toward more specific pain-point phrasing and re-run manually before waiting on the scheduler.

## Cross-Repo Slash Commands
These work from this repo via GitHub MCP:
- `/tool` — register or update Trend Detector on modrynstudio.com (opens PR on modryn-studio-v2)
- `/log` — draft a build log post for modrynstudio.com (opens PR on modryn-studio-v2)
