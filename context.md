
CONTEXT: Trend Detector

WHO I AM:
Luke — one-person studio, modrynstudio.com. I build tools targeting
trending search markets. I ship fast using AI-assisted development.

WHAT THIS PROJECT IS:
A private trend detection pipeline I run for myself.
Problem it solves: every morning I need to decide what to build next.
This script answers that question with data instead of gut feel.

PHASE 1 — PRIVATE PIPELINE (this repo):
A Python cron job that runs daily, pulls rising search trends from 3
sources, cross-references them, scores them, and writes a JSON file I
read over morning coffee. Zero public-facing infrastructure. Zero cost.

PHASE 2 — PUBLIC TOOL (future, separate repo):
Trend Detector becomes a public web tool: user enters a niche → tool
shows rising trends scored by velocity, volume, and buildability →
returns "here are 5 tools worth building this month."
Indie hackers would pay for this. Built on modryn studio's boilerplate.
Note: Google Trends official API access (on waitlist) is a nice-to-have
for scaling Phase 2, but is NOT a blocker. The 3-layer source architecture
already provides better signal quality than the official API would.

THE 3-LAYER PIPELINE:

Source 1: trendspy
  - Real-time trending via Google's internal API (same data Google uses)
  - 2-3 API calls per run (vs 24-30 with the old pytrends approach)
  - No auth, no waitlist, pure requests
  - Key calls: trending_now(geo='US'), trending_now_showcase_timeline()
  - File: fetcher.py

Source 2: Google Trends RSS
  - URL: https://trends.google.com/trending/rss?geo=US
  - Public feed, no auth, updated frequently
  - stdlib XML parse — no new dependencies
  - Provides: keyword, approx_traffic, pubDate, related news articles
  - File: rss_fetcher.py

Source 3: Gmail newsletter
  - Google Trends Daily Trending email (subscribed)
  - IMAP + app password (credentials in .env, never committed)
  - BeautifulSoup parse — only new dependency vs stdlib
  - Provides: trend clusters, growth %, categories, editorial curation
    that neither trendspy nor RSS offers
  - File: email_ingest.py
  - One-time setup: Google Account → App Passwords → generate for "Mail"

CROSS-REFERENCE ENGINE:
  - Normalize keywords (lowercase + strip)
  - Group by keyword across all 3 sources
  - Score boost: +20 for 2 sources, +40 for 3 sources
  - Output: data/signals_YYYY-MM-DD.json

WHY THIS MATTERS:
  - 1 source = a trend is happening
  - 2+ sources = a trend is real and worth acting on
  - trendspy catches it fast, RSS confirms volume, email provides
    context (growth %, category, related queries) that pure API data
    can't give you

DECISION SIGNAL:
  High-confidence signal = keyword appears in 2+ sources + Reddit/HN
  complaint about the problem = build it this week.

OUTPUT FORMAT (data/signals_YYYY-MM-DD.json):
  [
    {
      "keyword": "friend app",
      "score": 85,
      "sources": ["trendspy", "email"],
      "source_count": 2,
      "traffic": 5000,
      "growth": "+290%",
      "related": ["how to make friends after college"],
      "first_seen": "2026-03-01"
    },
    ...
  ]

KEEP ALL DAILY OUTPUT FILES — the history IS the product demo.
"I ran this privately for 3 months" is a better launch story than
launching cold. signals_2026-02-26.json, signals_2026-03-01.json — keep them all.

THE STACK:
- Python 3.12+
- trendspy (replaced pytrends-modern — 2-3 calls vs 24-30, no SSL hangs)
- beautifulsoup4 (for email parse)
- python-dotenv (for .env credentials)
- openai (GPT-5 Mini with Structured Outputs for cluster renaming + BUILD/WATCH/SKIP)
- Google Custom Search JSON API (competitor check, 100 free queries/day)
- schedule or Windows Task Scheduler for daily automation
- No database — flat JSON files in /data
- No server — runs locally

CLI FLAGS (pipeline.py):
  --trendspy   trendspy source only
  --rss        RSS source only
  --email      email source only
  --all        all 3 sources + cross-reference (default)
  --no-series      skip time-series enrichment (faster)
  --no-competitor  skip competitor check (faster)
  --no-reddit      skip Reddit validation (faster)
  (no flags)   same as --all

CRON SCHEDULE:
  9:00 AM daily (Windows Task Scheduler, StartWhenAvailable)
  Output written to data/signals_YYYY-MM-DD.json
  Logs written to logs/pipeline_YYYY-MM-DD.log

MORNING WORKFLOW:
  9:00 AM     cron runs pipeline.py --all
  9:02 AM     data/signals_YYYY-MM-DD.json written, top 5 printed to log
  Morning     open the file, scan top 5
  Decide      "I'm building X this week"

THE SCORING ALGORITHM:
  Score each trend 0-100 based on:
  - velocity     — how fast it's rising (week-over-week delta)
  - volume       — absolute search interest
  - buildability — can a solo dev build something useful in 48h?
                   (heuristic, hand-tuned, refine over time)
  - freshness    — has this already peaked? penalize if so
  - source_count — multi-source confidence boost (+20/+40)

CORE PRINCIPLES:
  - Solve your own problem first — you are the user
  - Keep it boring: one script, one output file, one cron job
  - No premature optimization
  - Version every output file — the history IS the product

FUTURE PHASE 2 ROUTES (not built yet):
  /                   → Hero + "enter your niche" input
  /results/[query]    → Scored trend list for that niche
  /about              → The private pipeline backstory
  /pricing            → When monetization is decided
