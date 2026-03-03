"""
rss_fetcher.py — Google Trends RSS feed (Source 2)

Pulls the public Daily Search Trends RSS feed for the US.
No auth, no API key, no dependencies beyond stdlib + requests.

Feed: https://trends.google.com/trending/rss?geo=US

Each <item> has a keyword, approximate traffic volume, publication date,
and related news articles. We parse into the same dict shape the pipeline
expects so cross-referencing with trendspy data is trivial.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

RSS_URL = "https://trends.google.com/trending/rss?geo=US"
HT_NS = {"ht": "https://trends.google.com/trending/rss"}

# Fake a browser UA — Google sometimes 403s bare urllib
_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:120.0)"}

_LOG_DIR = Path(__file__).parent / "logs"


def _write_error_log(message: str) -> None:
    """Append a timestamped error to logs/errors.log (same file as email_ingest)."""
    try:
        _LOG_DIR.mkdir(exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(_LOG_DIR / "errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{ts}] [rss] {message}\n")
    except OSError:
        pass


def _parse_traffic(raw: str) -> int:
    """'500,000+' → 500000, '1,000+' → 1000, non-numeric → 0."""
    if not raw:
        return 0
    try:
        return int(raw.replace(",", "").replace("+", "").strip())
    except ValueError:
        return 0


def _parse_news_items(item: ET.Element) -> list[dict]:
    """Extract related news articles from an RSS <item>."""
    articles = []
    for ni in item.findall("ht:news_item", HT_NS):
        title = (ni.findtext("ht:news_item_title", "", HT_NS) or "").strip()
        url = (ni.findtext("ht:news_item_url", "", HT_NS) or "").strip()
        source = (ni.findtext("ht:news_item_source", "", HT_NS) or "").strip()
        if title and url:
            articles.append({"title": title, "url": url, "source": source})
    return articles


def fetch_rss(geo: str = "US") -> list[dict]:
    """
    Fetch and parse the Google Trends RSS feed.

    Returns a list of dicts:
      {
        "keyword":       str,
        "approx_traffic": int,
        "source":        "rss",
        "pub_date":      str (ISO),
        "related_news":  [{"title", "url", "source"}, ...],
        "fetched_at":    str (ISO),
      }
    """
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    req = Request(url, headers=_HEADERS)
    try:
        with urlopen(req, timeout=15) as resp:
            xml_bytes = resp.read()
    except Exception as e:
        msg = f"Fetch failed: {e}"
        print(f"[rss] {msg}")
        _write_error_log(msg)
        return []

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        msg = f"XML parse failed: {e}"
        print(f"[rss] {msg}")
        _write_error_log(msg)
        return []
    now = datetime.now(timezone.utc).isoformat()

    results: list[dict] = []
    for item in root.iter("item"):
        keyword = (item.findtext("title") or "").strip()
        if not keyword:
            continue

        traffic_str = item.findtext("ht:approx_traffic", "0", HT_NS)
        pub_date_raw = item.findtext("pubDate", "")

        # Parse RFC-822 date → ISO
        pub_date = ""
        if pub_date_raw:
            try:
                from email.utils import parsedate_to_datetime
                pub_date = parsedate_to_datetime(pub_date_raw).isoformat()
            except Exception:
                pub_date = pub_date_raw

        results.append({
            "keyword":        keyword,
            "approx_traffic": _parse_traffic(traffic_str),
            "source":         "rss",
            "pub_date":       pub_date,
            "related_news":   _parse_news_items(item),
            "fetched_at":     now,
        })

    return results


# --- Standalone test ---
if __name__ == "__main__":
    trends = fetch_rss()
    print(f"Fetched {len(trends)} trends from RSS\n")
    for t in trends[:10]:
        news_count = len(t["related_news"])
        print(f"  {t['keyword']:<40}  traffic={t['approx_traffic']:>10,}  news={news_count}")
