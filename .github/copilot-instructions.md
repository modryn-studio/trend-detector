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
- **trendspy** (`pip install trendspy`) — uses Google's internal protobuf Trends API. 1 call returns 400+ trending topics with volume, growth %, and category. No selenium, no browser automation, no hidden dependencies.
- Windows Task Scheduler (6 AM daily)
- Flat JSON files in `/data` — no database

## Project Structure
```
pipeline.py          ← entry point, run this
fetcher.py           ← Stage 1: trending_now() + interest_over_time()
scorer.py            ← Stage 2: filter noise + score 0–100
data/
  trends_YYYY-MM-DD.json   ← daily output, NEVER delete these
requirements.txt
.gitignore           ← gitignore .env but NOT /data — keep all history
```

## Output Format
```json
{
  "date": "2026-03-01",
  "trends": [
    {
      "keyword": "bitcoin atm",
      "score": 64,
      "velocity": "rising",
      "volume": "medium",
      "buildability": "high",
      "category": "finance",
      "_raw": {
        "growth_score": 66.7,
        "volume_score": 40.0,
        "buildability_score": 50.0,
        "freshness_score": 100.0,
        "google_volume": 10000,
        "google_growth_pct": 1000
      }
    }
  ]
}
```

## Stage 1 — Discover (trending_now)
One API call. No seeds. Google tells us what's rising.
```python
from trendspy import Trends
tr = Trends(request_delay=2)
trends = tr.trending_now(geo='US')  # 400+ topics, <2 seconds
```
Each result includes `.keyword`, `.volume`, `.volume_growth_pct`, `.topics` (Google's category IDs), `.trend_keywords` (related queries).

We filter to topics we care about via `TOPIC_MAP`:
```python
TOPIC_MAP = {
    18: "technology",
    3:  "finance",
    7:  "health",
}
```

## Stage 2 — Filter + Score
Noise filtering is the value-add layer. Google gives us raw trending data; we strip everything that isn't a buildable opportunity.

**Noise categories:**
- Brand names (chatgpt, tesla, netflix, etc.)
- Generic terms (ai, productivity, personal finance)
- News/events (shooting, earthquake, election)
- Sports (vs, score, nba, playoff)
- Entertainment (movie, show, episode, concert)
- Person names (2-word all-alpha → likely celebrity/politician)

**Scoring weights:**
| Signal | Weight | Source |
|--------|--------|--------|
| Growth % | 35% | Google's trending_now data (no API call needed) |
| Buildability | 25% | Keyword heuristic (tool, app, tracker → high) |
| Volume | 20% | Google's trending_now data |
| Freshness | 20% | Time series peak position (requires interest_over_time) |

## Time Series Enrichment
After filtering+scoring, we fetch `interest_over_time` for the top ~15 surviving keywords (batched 5 per call = 3 API calls). This gives us a 30-day time series to compute freshness — has this trend already peaked?

Total API calls per run: **~4** (1 trending_now + 3 interest_over_time batches).

## Why Not Seeds?
The original pipeline used manually crafted seed keywords per category, then called `related_queries` to discover rising terms. This approach:
1. Required constant seed tuning (pain-point phrasing vs informational queries)
2. Made 24-30 API calls per run → guaranteed 429 rate limits
3. Caused SSL hangs on Windows → required multiprocessing kill hacks

`trending_now()` eliminates all three problems. Google does the discovery; we filter and score.

## Code Style
- Write as a senior engineer: minimal surface area, obvious naming
- Comments explain WHY, not what
- One file = one responsibility
- Early returns for error handling
- Never add complexity before Phase 2 requires it

## Cross-Repo Slash Commands
These work from this repo via GitHub MCP:
- `/tool` — register or update Trend Detector on modrynstudio.com (opens PR on modryn-studio-v2)
- `/log` — draft a build log post for modrynstudio.com (opens PR on modryn-studio-v2)
