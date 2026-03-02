
# Trend Detector

Private trend detection pipeline. Runs daily, scores rising search trends, outputs a JSON file and a plain-English morning briefing.

**Data sources (3-layer):**
1. **trendspy** — real-time trending via Google's internal API (no auth, no waitlist)
2. **Google Trends RSS** — `trending/rss?geo=US` (public, stdlib XML parse)
3. **Gmail newsletter** — Google Trends daily email parsed via IMAP + BeautifulSoup

Trends appearing in 2+ sources get a confidence boost. Keywords are filtered, scored, clustered into macro-themes, validated against Reddit, and analyzed into a morning briefing.

**Pipeline stages:**
1. Collect from all 3 sources
2. Cross-reference — merge duplicates; multi-source hits get +20/+40 confidence boost
3. Filter — strip brands, sports, entertainment, news events, person names
4. Score — 0–100 composite (35% growth velocity, 25% buildability, 20% volume, 20% freshness)
5. Cluster — group by newsletter section headers, then by shared stemmed tokens
6. Reddit validate — targeted subreddit search + pain-framed queries
7. Competitor check — two-pass Brave Search:
   - Pass 1 (keyword-based): GREEN/YELLOW/RED/INCONCLUSIVE on raw trend keyword. RED + no pain → SKIP immediately, no LLM call.
   - Pass 2 (build-idea-based): LLM generates 3 tool-focused queries from its build idea; Brave searches those to verify the specific product doesn't already exist.
8. Time-series enrich — `interest_over_time()` for top ~15 keywords; updates freshness score
9. Report — LLM renames clusters by human need, generates BUILD/WATCH/SKIP decisions with emotional-barrier guidance, adds lifecycle tags (`EARLY`/`PEAKING`/`FADING`)

**Output:**
- `data/signals_YYYY-MM-DD.json` — full structured output (clusters + scores + Reddit + competition)
- `briefings/briefing_YYYY-MM-DD.md` — plain-English: cluster table, the story, BUILD/WATCH/SKIP decisions

**Scheduling:** `run_daily.bat` runs via Windows Task Scheduler at 9:00 AM daily.

**Phase 2: public web tool** — when signal quality is proven over several months of private runs.
