
CONTEXT: Trend Detector

WHO I AM:
Luke — one-person studio, modrynstudio.com. I build tools targeting
trending search markets. I ship fast using AI-assisted development.

WHAT THIS PROJECT IS:
A private trend detection pipeline I run for myself daily.
Problem it solves: every morning I need to decide what to build next.
This pipeline answers that question with data instead of gut feel.

PHASE 1 — PRIVATE PIPELINE (this repo):
A Python script that runs via Windows Task Scheduler at 9 AM, pulls
rising search trends from 3 sources, cross-references them, scores
them, clusters them, validates against Reddit, checks competitors,
and writes a morning briefing I read over coffee. Zero public-facing
infrastructure. Zero cost beyond API keys I already have.

PHASE 2 — PUBLIC TOOL (future, separate repo):
Trend Detector becomes a public web tool: user enters a niche → tool
shows rising trends scored by velocity, volume, and buildability →
returns "here are 5 tools worth building this month."
Indie hackers would pay for this. Built on modryn studio's Next.js
boilerplate. Don't build Phase 2 infrastructure here.

THE 3-LAYER PIPELINE (sources):

Source 1: trendspy (fetcher.py)
  - Google's internal protobuf Trends API — same data Google uses
  - 1 call = 400+ trending topics, no auth, no selenium
  - Key calls: trending_now(geo='US'), interest_over_time()
  - Categories tracked: technology, finance, health, hobbies, education

Source 2: Google Trends RSS (rss_fetcher.py)
  - URL: https://trends.google.com/trending/rss?geo=US
  - Public feed, no auth, stdlib XML parse (no new dependencies)
  - Provides: keyword, approx_traffic, pubDate, related news articles

Source 3: Gmail newsletter (email_ingest.py)
  - Google Trends Daily Trending email (subscribed)
  - IMAP + app password (credentials in .env, never committed)
  - BeautifulSoup HTML parse
  - Provides: editorial section headers (Google's own cluster groupings),
    growth %, categories — context neither trendspy nor RSS offers

PIPELINE STAGES (in order):
  1. Collect       — fetch from all 3 sources
  2. Cross-ref     — merge same keyword seen across sources; multi-source
                     gets a confidence boost (+20 for 2 sources, +40 for 3)
  3. Filter        — is_buildable() strips brands, sports, entertainment,
                     news events, person names, single generic words
  4. Score         — 0-100 composite (see weights below)
  5. Cluster       — Pass 1: group by email section header (Google's own
                     groupings). Pass 2: group by shared stemmed tokens.
  6. Reddit        — targeted subreddit search; flag pain signals
  7. Competitor    — two-pass Brave Search (see below)
  8. Time series   — interest_over_time() enrichment; updates freshness;
                     re-sorts clusters
  9. Briefing      — GPT-5.2 renames clusters by human need, generates
                     BUILD/WATCH/SKIP decisions, writes
                     briefings/briefing_YYYY-MM-DD.md

COMPETITOR CHECK (competitor_check.py):
  Pass 1 (keyword-based): checks trend keyword + suffix variants for top 5
    clusters. Verdict: GREEN / YELLOW / RED / INCONCLUSIVE.
    RED gate: RED + no confirmed Reddit pain → emit SKIP, skip LLM.
    Score gate: score < 50 + no confirmed pain → SKIP (enforced in code).
  Pass 2 (build-idea-based): LLM outputs 3 competition_queries for its
    specific build idea; Brave searches those to check the product doesn't
    already exist. Only runs for BUILD/WATCH decisions. BUILD→WATCH if
    refined verdict is RED.

SCORING WEIGHTS:
  Growth %     35%  — trending_now growth_pct / email growth string
  Buildability 25%  — keyword heuristic (tool, app, tracker, calculator)
  Volume       20%  — trending_now volume (email/RSS = neutral 50, not penalized)
  Freshness    20%  — interest_over_time peak position

OUTPUTS:
  data/signals_YYYY-MM-DD.json     — full structured output (NEVER delete)
  briefings/briefing_YYYY-MM-DD.md — morning briefing in plain English

OUTPUT FORMAT (data/signals_YYYY-MM-DD.json):
  {
    "date": "2026-03-04",
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
        "source": "trendspy",
        "source_count": 1,
        "category": "finance",
        "_raw": { "google_growth_pct": 1000, "google_volume": 10000 }
      }
    ],
    "competition": {
      "friend app": { "verdict": "GREEN", "competitor_count": 1, "top_competitors": [...] }
    },
    "decisions": {
      "Making Friends": {
        "decision": "BUILD",
        "confidence": "HIGH",
        "build_idea": "...",
        "target_slug": "...",
        "context_seed": {
          "product_description": "...",
          "target_user": "...",
          "emotional_barrier": "...",
          "routes": ["/ → ..."]
        }
      }
    }
  }

KEEP ALL DAILY OUTPUT FILES — the history IS the product demo.
"I ran this privately for 3 months" is a better launch story than
launching cold. signals_2026-02-26.json, signals_2026-03-01.json — keep them all.

THE STACK:
- Python 3.12+
- trendspy (Google's internal protobuf API, no auth)
- beautifulsoup4 (email newsletter HTML parse)
- python-dotenv (.env credentials)
- openai (GPT-5.2 with Structured Outputs — cluster rename + BUILD/WATCH/SKIP + context_seed)
- Brave Search API (competitor check, 1,000 free queries/month)
- Windows Task Scheduler (9 AM daily via run_daily.bat)
- No database — flat JSON files in /data
- No server — runs locally

ENV (.env, gitignored):
  OPENAI_API_KEY
  BRAVE_SEARCH_KEY
  GMAIL_ADDRESS
  GMAIL_APP_PASSWORD

CLI FLAGS (pipeline.py):
  (no flags)       all 3 sources — default for scheduled run
  --trendspy       trendspy only (debugging)
  --rss            RSS only (debugging)
  --email          email only (debugging)
  --no-series      skip time-series enrichment (faster)
  --no-competitor  skip competitor check (faster)
  --no-reddit      skip Reddit validation (faster)

CRON SCHEDULE:
  9:00 AM daily (Windows Task Scheduler, StartWhenAvailable)
  Entry point: run_daily.bat → .venv/Scripts/python.exe pipeline.py
  Output: data/signals_YYYY-MM-DD.json
  Briefing: briefings/briefing_YYYY-MM-DD.md
  Logs: logs/pipeline_YYYY-MM-DD.log

MORNING WORKFLOW:
  9:00 AM     Task Scheduler runs pipeline.py
  ~9:02 AM    briefings/briefing_YYYY-MM-DD.md written
  Morning     open briefing, read BUILD decisions
  Decide      "I'm building X this week"

DECISION SIGNAL:
  BUILD  = strong demand + confirmed Reddit pain + market gap (GREEN/YELLOW)
  WATCH  = demand present but competition saturated or signal weak
  SKIP   = RED competitor gate, or score < 50 with no confirmed pain

context_seed in BUILD decisions pre-fills context.md for the build phase:
  product_description, target_user, emotional_barrier, routes

CORE PRINCIPLES:
  - Solve your own problem first — you are the user
  - Keep it boring: one script, one output file, one scheduler job
  - No premature optimization
  - Version every output file — the history IS the product
  - Never add complexity before Phase 2 requires it

FUTURE PHASE 2 ROUTES (not built yet):
  /                   → Hero + "enter your niche" input
  /results/[query]    → Scored trend list for that niche
  /about              → The private pipeline backstory
  /pricing            → When monetization is decided
