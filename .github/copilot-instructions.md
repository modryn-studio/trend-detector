# Trend Detector — Copilot Context

## What This Is
A private Python pipeline that runs daily, pulls rising search trends via pytrends, scores them, and writes a JSON file Luke reads every morning to decide what to build next. No web server. No database. No users. Just a script and flat files.

## Phase 1 (this repo) — Private Pipeline
- One script: `pipeline.py`
- Runs on a cron job at 6:00 AM daily
- Output: `data/trends_YYYY-MM-DD.json`
- Keep ALL output files — the history becomes the Phase 2 demo

## Phase 2 (future, separate repo) — Public Tool
When Google Trends API alpha access arrives, this becomes a public web tool built on modryn-studio's Next.js boilerplate. Don't build Phase 2 infrastructure here.

## Stack
- Python 3.12+
- pytrends (scraping bridge — fragile at scale, fine for solo daily use)
- System cron or `schedule` library
- Flat JSON files in `/data` — no database

## Project Structure
```
pipeline.py          ← entry point, run this
scorer.py            ← scoring logic (velocity, volume, buildability, freshness)
fetcher.py           ← pytrends wrapper
data/
  trends_YYYY-MM-DD.json   ← daily output, never delete
requirements.txt
.env                 ← any API keys (gitignored)
```

## Output Format
```json
[
  {
    "keyword": "...",
    "score": 87,
    "velocity": "rising",
    "volume": "medium",
    "buildability": "high",
    "category": "productivity"
  }
]
```

## Scoring Algorithm
Score each trend 0–100:
- **velocity** — week-over-week rise delta
- **volume** — absolute search interest
- **buildability** — can a solo dev ship something useful in 48h? (heuristic, hand-tuned)
- **freshness** — penalize trends that have already peaked

Start with simple weights. Tune as you observe which trends produce good tool ideas.

## Categories
`productivity`, `ai-tools`, `developer-tools`, `finance`, `health`, `creator-tools`

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
