
# Trend Detector

Private trend detection pipeline. Runs daily, scores rising search trends, outputs a JSON file.

**Data sources (3-layer):**
1. **trendspy** — real-time trending via Google's internal API (no auth, no waitlist)
2. **Google Trends RSS** — `trending/rss?geo=US` (public, stdlib XML parse)
3. **Gmail newsletter** — Google Trends daily email parsed via IMAP + BeautifulSoup

Trends appearing in 2+ sources get a confidence boost. Output: `data/signals_YYYY-MM-DD.json`.

**Phase 2: public web tool** — when signal quality is proven over several months of private runs.
Google Trends official API access (on waitlist) is a nice-to-have for Phase 2, not a blocker.
