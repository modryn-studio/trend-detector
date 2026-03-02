# How It Works

## Daily routine

Every morning at 9AM, Windows Task Scheduler runs the pipeline automatically. No action needed.

Open `briefings/briefing_YYYY-MM-DD.md` in VS Code and press `Ctrl+Shift+V` to read the rendered output.

## Manual run

If you need to run it before 9AM or re-run for any reason:

```
python pipeline.py
```

No flags needed — the default runs all 3 sources. Single-source flags (`--trendspy`, `--rss`, `--email`) exist for debugging.

---

## What the pipeline does

| Stage | What happens |
|---|---|
| **Collect: trendspy** | Hits Google's internal trends API — returns 400+ trending topics with volume and growth % |
| **Collect: RSS** | Pulls Google's public trending RSS feed (`trends.google.com/trending/rss?geo=US`) |
| **Collect: Gmail** | Logs into Gmail via IMAP, reads any new Google Trends newsletters (last 7 days) |
| **Cross-reference** | Merges the same keyword seen across multiple sources — multi-source hits get a confidence boost (+20 for 2 sources, +40 for 3) |
| **Filter** | Strips brands, sports, entertainment, news events, person names, and single generic words |
| **Score** | Scores each keyword 0–100: 35% growth velocity, 25% buildability, 20% volume, 20% freshness |
| **Cluster** | Groups keywords into macro-trend clusters using Google's newsletter section headers first, then shared keyword tokens |
| **Reddit** | Searches targeted subreddits with pain-framed queries for top clusters — checks for frustration/need signals |
| **Competitor check (Pass 1)** | Brave Search on raw trend keyword — how many purpose-built tools already exist? GREEN/YELLOW/RED/INCONCLUSIVE. If RED and no Reddit pain signal, cluster is immediately SKIP — no LLM call. |
| **Competitor check (Pass 2)** | LLM proposes a build idea and generates 3 tool-focused search queries. Brave searches those to check if that *specific product* already exists. Results shown separately as "(build-idea check)". |
| **Time series** | Fetches 30-day trend data for top ~15 keywords to refine freshness scores |
| **Briefing** | LLM renames clusters by human need, generates BUILD/WATCH/SKIP decisions, writes `briefings/briefing_YYYY-MM-DD.md` |

Total API calls per run: ~13 (1 trending_now + ~3 interest_over_time + ~3 Reddit + ~5 Brave Search + ~2 Brave refined + ~2 OpenAI). The RED gate typically saves 2–3 LLM calls/day.

---

## Output files

| File | What it is |
|---|---|
| `data/signals_YYYY-MM-DD.json` | Full structured output — never delete these, they become the Phase 2 dataset |
| `briefings/briefing_YYYY-MM-DD.md` | Plain-English morning briefing — this is what you read |
| `logs/pipeline_YYYY-MM-DD.log` | Full run log — check here if a briefing doesn't appear |

---

## If something goes wrong

- **No briefing file today** — check `logs/pipeline_YYYY-MM-DD.log` for the error
- **PC was off at 9AM** — Task Scheduler has `StartWhenAvailable` enabled; it will run automatically when the machine wakes up
- **trendspy or RSS fails** — those stages return empty and the pipeline continues with whatever sources did work
- **Gmail IMAP error** — app password may have expired; generate a new one at myaccount.google.com → Security → App passwords, update `.env`