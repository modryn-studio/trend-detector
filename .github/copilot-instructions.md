# Trend Detector — Copilot Context

## What This Is
A private Python pipeline that runs daily, pulls rising search trends, scores them, groups them into macro-trend clusters, and writes a JSON file Luke reads every morning to decide what to build next. No web server. No database. No users. Just scripts and flat files.

## Phase 1 (this repo) — Private Pipeline
- Entry point: `pipeline.py`
- Runs via Windows Task Scheduler at 9:00 AM daily (`run_daily.bat`)
- Output: `data/signals_YYYY-MM-DD.json`
- Keep ALL output files — the history becomes the Phase 2 demo dataset

## Phase 2 (future, separate repo) — Public Tool
When signal quality is proven over several months of private runs, this becomes a public web tool on modryn-studio's Next.js boilerplate. Don't build Phase 2 infrastructure here.

## Stack
- Python 3.12+
- **trendspy** — Google's internal protobuf Trends API. 1 call = 400+ trending topics. No auth, no selenium.
- **beautifulsoup4** — Gmail newsletter HTML parsing
- **python-dotenv** — `.env` for credentials
- **openai** — GPT-5.2 with Structured Outputs for cluster renaming + BUILD/WATCH/SKIP decisions + context_seed
- **Brave Search API** — competitor check (1,000 free queries/month; Google CSE closed to new customers Feb 2026)
- Windows Task Scheduler (9 AM daily)
- Flat JSON files in `/data` — no database

## Google Cloud Project: modryn-trends
GCP project `modryn-trends` (org: modrynstudio.com, ID: 147653796077) exists for one reason:
Luke applied for alpha access to the **Google Search Trends API** (official, not trendspy):
https://developers.google.com/search/apis/trends#apply
The application requires a GCP project ID. If/when alpha access is granted, this project is where it gets provisioned.
**Do not delete this project.** trendspy is the current data source; the official API would replace or supplement it.

## Project Structure

GitHub repo: `modryn-studio/trend-detector`  
Venv: `.venv/` (e.g. `.venv/Scripts/python.exe pipeline.py`)

```
pipeline.py          ← entry point, orchestrates all stages
fetcher.py           ← Source 1: trendspy trending_now() + interest_over_time()
rss_fetcher.py       ← Source 2: Google Trends RSS feed (stdlib XML, no auth)
email_ingest.py      ← Source 3: Gmail IMAP, parses Google Trends newsletters
scorer.py            ← noise filter + 0–100 composite score
cluster.py           ← groups keywords into macro-trend clusters
reddit_check.py      ← validates top clusters against Reddit (targeted subreddits)
competitor_check.py  ← Brave Search competitor check (GREEN/YELLOW/RED)
reporter.py          ← LLM-powered briefing: cluster rename + BUILD/WATCH/SKIP
run_daily.bat        ← Windows Task Scheduler entry point
data/
  signals_YYYY-MM-DD.json  ← daily output, NEVER delete these
briefings/
  briefing_YYYY-MM-DD.md   ← daily morning briefing, auto-generated
.env                 ← GMAIL_ADDRESS, GMAIL_APP_PASSWORD, OPENAI_API_KEY,
                       BRAVE_SEARCH_KEY (gitignored)
```

## Running the Pipeline

```
python pipeline.py          # all 3 sources (default — no flags needed)
python pipeline.py --trendspy   # trendspy only (debugging)
python pipeline.py --rss        # RSS only (debugging)
python pipeline.py --email      # email only (debugging)
python pipeline.py --no-series  # skip time-series enrichment (faster)
python pipeline.py --no-competitor  # skip competitor check (faster)
```

The scheduled run (`run_daily.bat`) also uses no flags — relies on the default.
Output is always `data/signals_YYYY-MM-DD.json` regardless of which sources ran.

## Pipeline Stages
```
trendspy ─┐
RSS      ─┼─► cross-ref ─► filter ─► score ─► cluster ─► Reddit ─► competitor ─► time series ─► JSON ─► briefing
Gmail    ─┘
```

1. **Collect** — fetch from all 3 sources
2. **Cross-reference** — merge same keyword seen across sources; multi-source hits get a confidence boost (+20 for 2 sources, +40 for 3)
3. **Filter** — `is_buildable()` strips brands, sports, entertainment, news events, person names, single generic words
4. **Score** — 0–100 composite: 35% growth velocity, 25% buildability, 20% volume, 20% freshness
5. **Cluster** — Pass 1: group by email newsletter section header (Google's own groupings). Pass 2: group by shared stemmed tokens. No hardcoded synonym maps — must work for any topic regime.
6. **Reddit validate** — targeted subreddit search + pain-framed queries; flag pain signals
7. **Competitor check** — two-pass Brave Search:
   - Pass 1 (keyword-based): checks raw trend keyword + suffix variants; GREEN/YELLOW/RED/INCONCLUSIVE. RED + no Reddit pain → emit SKIP immediately, skip LLM entirely (RED gate).
   - Pass 2 (build-idea-based): LLM outputs 3 `competition_queries` derived from its build idea; Brave searches those to verify the specific product doesn't already exist. Results stored under cluster name + "(build-idea check)". BUILD → WATCH if refined=RED.
   - Note: `_find_pass1_competition()` searches all member keywords for pass-1 data — survives `top_keyword` shifts from time-series enrichment.
8. **Time series enrich** — `interest_over_time()` for top ~15 keywords; updates freshness score; re-sorts clusters after enrichment
9. **Report** — `reporter.py`: LLM (GPT-5.2) renames clusters by human need, generates BUILD/WATCH/SKIP decisions with structured outputs, writes `briefings/briefing_YYYY-MM-DD.md`. LLM prompt includes emotional-barrier guidance ("build for the feeling that stops someone from acting, not the information gap") and builder-capacity calibration (multi-file systems, 3-6 API integrations, full Next.js + Stripe deploys — not static cheat sheets). Structured output includes `context_seed` (product_description, target_user, emotional_barrier, routes) to pre-fill the boilerplate's `context.md` during build phase. Cluster table includes lifecycle tags (`EARLY`/`PEAKING`/`FADING`) derived from freshness scores.

Total API calls per run: **~13** (1 trending_now + ~3 batched interest_over_time + ~3 Reddit searches + ~5 Brave Search + ~2 Brave refined + ~2 OpenAI)
RED gate typically saves 2-3 LLM calls/day (obvious news/brand topics never reach the LLM).

## Output Format
```json
{
  "date": "2026-03-01",
  "sources": ["trendspy", "rss", "email"],
  "clusters": [
    {
      "cluster_name": "Making Friends",
      "cluster_score": 82,
      "member_count": 4,
      "top_keyword": "friend app",
      "growth_signals": ["breakout", "+290%"],
      "members": [...],
      "reddit": { "total_posts": 12, "pain_signal": true, "top_posts": [...] }
    }
  ],
  "unclustered": [
    {
      "keyword": "bitcoin atm",
      "score": 71,
      "category": "finance",
      "_raw": { "google_growth_pct": 1000, "google_volume": 10000 }
    }
  ],
  "competition": {
    "friend app": { "verdict": "GREEN", "competitor_count": 1, "top_competitors": [...] }
  },
  "decisions": {
    "Making Friends": {
      "decision": "BUILD", "confidence": "HIGH",
      "build_idea": "...", "target_slug": "...",
      "context_seed": {
        "product_description": "...",
        "target_user": "...",
        "emotional_barrier": "...",
        "routes": ["/ → ..."]
      }
    }
  }
}
```

## Noise Filter Rules (scorer.py)
- Brand names (chatgpt, tesla, netflix, wsj, cnn, fox…)
- Generic terms (ai, productivity, personal finance)
- News/events (shooting, earthquake, election)
- Sports (vs, score, nba, playoff, basketball, football…)
- Entertainment (movie, show, episode, concert)
- Person names — 2-word all-alpha → likely celebrity/politician; single-word all-alpha without tool-intent suffix → filtered
- Single-word all-alpha with no tool-intent signal

## Scoring Weights
| Signal | Weight | Source |
|--------|--------|--------|
| Growth % | 35% | trending_now growth_pct / email growth string |
| Buildability | 25% | Keyword heuristic (tool, app, tracker, calculator → high) |
| Volume | 20% | trending_now volume (email/RSS volume=0 → neutral 50, not penalized) |
| Freshness | 20% | interest_over_time peak position |

## Clustering Rules (cluster.py)
- `SKIP_CATEGORIES = {"unknown", "technology", "finance", "health", ""}` — trendspy's generic category names don't form meaningful clusters
- Pass 1 min_size=2, Pass 2 min_size=3
- Cluster score = avg member score + size bonus (max +25) + growth bonus (max +15)
- No hardcoded synonym groups — must generalize across any topic domain

## Code Style
- Write as a senior engineer: minimal surface area, obvious naming
- Comments explain WHY, not what
- One file = one responsibility
- Early returns for error handling
- Never add complexity before Phase 2 requires it

## Cross-Repo Slash Commands
These work from this repo via GitHub MCP (target repo: `modryn-studio/modryn-studio-v2`):
- `/tool` — register or update Trend Detector on modrynstudio.com (opens PR on modryn-studio-v2)
- `/log` — draft a build log post for modrynstudio.com (opens PR on modryn-studio-v2)
