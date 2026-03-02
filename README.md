
# Trend Detector

Private trend detection pipeline. Runs daily, scores rising search trends, outputs a JSON file and a plain-English morning briefing.

**Data sources (3-layer):**
1. **trendspy** — real-time trending via Google's internal API (no auth, no waitlist)
2. **Google Trends RSS** — `trending/rss?geo=US` (public, stdlib XML parse)
3. **Gmail newsletter** — Google Trends daily email parsed via IMAP + BeautifulSoup

Trends appearing in 2+ sources get a confidence boost. Keywords are clustered into macro-themes, validated against Reddit, and analyzed into a morning briefing.

**Output:**
- `data/signals_YYYY-MM-DD.json` — full structured output (clusters + scores + Reddit)
- `briefings/briefing_YYYY-MM-DD.md` — plain-English: cluster table, the story, build opportunities

**Phase 2: public web tool** — when signal quality is proven over several months of private runs.
