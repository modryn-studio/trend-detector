CONTEXT: Trend Detector

WHO I AM:
Luke — one-person studio, modrynstudio.com. I build AI-first tools
targeting trending search markets. I ship fast using AI-assisted development.

WHAT THIS PROJECT IS:
A private trend detection pipeline I run for myself.
Problem it solves: every morning I need to decide what to build next.
This script answers that question with data instead of gut feel.

PHASE 1 — PRIVATE PIPELINE (this repo):
A Python cron job that runs daily, pulls rising search trends via pytrends,
scores them, and writes a JSON file I read over morning coffee.
Zero public-facing infrastructure. Zero cost. Ships in days.

PHASE 2 — PUBLIC TOOL (future, separate repo):
When Google Trends API alpha access arrives, Trend Detector becomes a
public web tool: user enters a niche → tool shows rising trends scored
by velocity, volume, and buildability → returns "here are 5 tools worth
building this month." Indie hackers would pay for this. Built on modryn
studio's boilerplate.

THE PHASE 1 PIPELINE:
Cron schedule:  6:00 AM daily
Script:         pipeline.py
Output:         data/trends_YYYY-MM-DD.json
Format:
  [
    {
      "keyword": "...",
      "score": 87,
      "velocity": "rising",
      "volume": "medium",
      "buildability": "high",
      "category": "productivity"
    },
    ...
  ]

Keep all daily output files — they become the demo and the scoring
validation story for Phase 2. "I ran this privately for 3 months"
is a better launch story than launching cold.

THE STACK (Phase 1):
- Python 3.12+
- pytrends (Google Trends scraping bridge — fragile at scale, fine for
  personal use at low frequency)
- schedule or system cron for scheduling
- No database — flat JSON files in /data
- No server — runs locally or on a cheap VPS

THE SCORING ALGORITHM:
Score each trend 0–100 based on:
- velocity     — how fast it's rising (week-over-week delta)
- volume       — absolute search interest
- buildability — can a solo dev build something useful in 48h?
                 (heuristic, hand-tuned, refine over time)
- freshness    — has this already peaked? penalize if so

Start simple. Tune the weights as you observe which trends actually
produce good tool ideas vs noise.

CATEGORIES TO TRACK (starting list, expand as needed):
- productivity
- ai-tools
- developer-tools
- finance
- health
- creator-tools

OUTPUT WORKFLOW:
6:00 AM     cron runs pipeline.py
6:02 AM     data/trends_YYYY-MM-DD.json written
Morning     open the file, scan top 5
Decide      "I'm building X this week"

CORE PRINCIPLES:
- Solve your own problem first — you are the user
- Keep it boring: one script, one output file, one cron job
- No premature optimization — if pytrends breaks, fix it then
- Version every output file — the history IS the product demo.
  trends_2026-02-26.json, trends_2026-02-27.json — keep them all.
  Three months from now: "Here's what I spotted in February that blew up
  in April" is a better sales page than any feature list.
- Don't add infrastructure until Phase 2

FUTURE PHASE 2 ROUTES (not built yet):
/                   → Hero + "enter your niche" input
/results/[query]    → Scored trend list for that niche
/about              → The private pipeline backstory
/pricing            → When monetization is decided
