"""
email_ingest.py — Google Trends newsletter parser (Source 3)

Connects to Gmail via IMAP, fetches unread Google Trends Daily Trending
newsletters, parses the narrative HTML to extract:
  - Trend keywords (quoted phrases)
  - Growth percentages (+290%, breakout, all-time high)
  - Category/section names (from h3/h4 headings or large-font styled spans)

Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env.
"""

import imaplib
import email as email_lib
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Sections to skip — entertainment/calendar noise
_SKIP_SECTIONS = {"mark your calendars", "notes"}

# Patterns to extract quoted keywords and growth signals
_QUOTE_RE = re.compile(r'[\u201c"]\s*([^"\u201d]{3,60}?)\s*[\u201d"]')

_GROWTH_RE = re.compile(
    r'[\u201c"]'              # opening quote
    r'\s*([^"\u201d]{3,60}?)' # keyword (3-60 chars)
    r'\s*[\u201d"]'           # closing quote
    r'([^"\u201c]{0,100}?'    # gap text (up to 100 chars before signal)
    r'(?:[+-][\d,]+%|all-time high|broke out|breakout))'
)


def _parse_growth(context: str) -> str:
    """Extract growth string from context text after a keyword."""
    pct = re.search(r'([+-][\d,]+%)', context)
    if pct:
        return pct.group(1)
    if "all-time high" in context.lower():
        return "all-time high"
    if "broke out" in context.lower() or "breakout" in context.lower():
        return "breakout"
    return ""


_LARGE_FONT_RE = re.compile(r'font-size\s*:\s*(\d+)pt', re.I)


def _is_section_header_span(tag) -> bool:
    """Return True if this tag is a large-font span used as a section header.

    Some newsletter editions use <p><span style="font-size:16pt..."> instead
    of <h3>/<h4> for sub-section titles. Detect by font-size >= 14pt on a
    span whose parent is a <p> with no other substantial text siblings.
    """
    if tag.name != "span":
        return False
    style = tag.get("style", "")
    m = _LARGE_FONT_RE.search(style)
    if not m or int(m.group(1)) < 14:
        return False
    # Must be the primary content of its parent <p>
    parent = tag.parent
    if not parent or parent.name != "p":
        return False
    text = tag.get_text(strip=True)
    return bool(text) and len(text.split()) <= 8  # headings are short


def _parse_newsletter_html(html: str) -> list[dict]:
    """Parse one newsletter's HTML into a list of trend dicts.

    Handles three observed newsletter layouts (may appear in same email):
      1. Format A (standard): section headers are <h3> tags containing a
         14pt Google-blue span — e.g. "Top Trends", "Making Friends"
      2. Format A sub-sections: <p><span style="font-size:16pt Google Sans">
         for topic clusters within a section — e.g. "Boy Kibble"
      3. Format B (older): section headers are <p><span style="font-size:19pt">
         in Google blue/green — e.g. "Spring Break", "Destinations"

    Note: Format B also uses <h4> tags for 12pt gray sub-labels
    ("Top trending 'spring break itinerary for…'") — these are NOT section
    headers and are intentionally excluded from detection.
    """
    soup = BeautifulSoup(html, "html.parser")
    trends: list[dict] = []
    seen_keywords: set[str] = set()

    # Collect all section-header nodes in document order.
    # Only <h3> (not <h4>) is treated as a section-header tag — Format B
    # newsletters use <h4> for short gray caption labels, not true headers.
    header_nodes = []
    for tag in soup.find_all(True):
        if tag.name == "h3":
            header_nodes.append(tag)
        elif _is_section_header_span(tag):
            # Use the parent <p> as the boundary node for sibling iteration
            header_nodes.append(tag.parent)

    if not header_nodes:
        full_text = soup.get_text(" ", strip=True)
        _extract_from_text(full_text, "general", trends, seen_keywords)
        return trends

    # Deduplicate while preserving order (span parent <p> may appear twice
    # if the same <p> was already added)
    seen_nodes: set[int] = set()
    unique_headers = []
    for node in header_nodes:
        if id(node) not in seen_nodes:
            seen_nodes.add(id(node))
            unique_headers.append(node)

    header_set = {id(n) for n in unique_headers}

    for node in unique_headers:
        category = node.get_text(strip=True)
        if category.lower() in _SKIP_SECTIONS:
            continue

        # Collect sibling text until the next section header
        text_parts: list[str] = []
        for sib in node.find_next_siblings():
            if id(sib) in header_set or sib.name in ("h3", "h4"):
                break
            # Also stop if we hit another large-font span header
            if sib.find(_is_section_header_span):
                break
            text_parts.append(sib.get_text(" ", strip=True))

        section_text = " ".join(text_parts)
        _extract_from_text(section_text, category, trends, seen_keywords)

    return trends


def _extract_from_text(text: str, category: str,
                       trends: list[dict], seen: set[str]) -> None:
    """Extract keyword-growth pairs from narrative text."""
    # First pass: keywords with explicit growth signals
    for m in _GROWTH_RE.finditer(text):
        kw = m.group(1).strip()
        kw_lower = kw.lower()
        if kw_lower in seen or len(kw) < 3:
            continue
        # Skip partial patterns like "... groups for adults"
        if kw.startswith("...") or kw.startswith("\u2026"):
            continue
        growth = _parse_growth(m.group(2))
        seen.add(kw_lower)
        trends.append({
            "keyword":  kw,
            "growth":   growth,
            "category": category,
            "source":   "email",
        })

    # Second pass: remaining quoted keywords without growth
    for m in _QUOTE_RE.finditer(text):
        kw = m.group(1).strip()
        kw_lower = kw.lower()
        if kw_lower in seen or len(kw) < 3:
            continue
        if kw.startswith("...") or kw.startswith("\u2026"):
            continue
        # Skip filler phrases
        if kw_lower in ("as an adult", "as an introvert", "as a teenager"):
            continue
        seen.add(kw_lower)
        trends.append({
            "keyword":  kw,
            "growth":   "",
            "category": category,
            "source":   "email",
        })


_LOG_DIR = Path(__file__).parent / "logs"


def _write_error_log(message: str) -> None:
    """Append a timestamped error to logs/errors.log.

    This file persists across runs so Task Scheduler failures are
    visible in one place without scanning per-day pipeline logs.
    """
    try:
        _LOG_DIR.mkdir(exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(_LOG_DIR / "errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")
    except OSError:
        pass  # Don't let logging failure mask the real error


def fetch_email(mark_read: bool = False) -> list[dict]:
    """
    Fetch and parse unread Google Trends newsletters from Gmail.

    Returns a flat list of trend dicts:
      { keyword, growth, category, source, email_date }

    If mark_read=True, marks processed emails as SEEN.
    """
    addr = os.getenv("GMAIL_ADDRESS")
    pw = os.getenv("GMAIL_APP_PASSWORD")

    if not addr or not pw:
        print("[email] GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set in .env")
        return []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(addr, pw)
    except imaplib.IMAP4.error as e:
        msg = f"[email] IMAP login failed: {e}"
        print(msg)
        # Write to persistent error log so Task Scheduler failures are visible
        # without scanning daily pipeline logs.
        _write_error_log(msg)
        return []

    mail.select("inbox")

    # Search for unread Google Trends newsletters
    status, data = mail.search(None, '(FROM "trends-noreply@google.com" UNSEEN)')
    if status != "OK" or not data[0]:
        # Fallback: recent emails (last 7 days) — avoids reprocessing full history
        since_str = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
        status, data = mail.search(
            None, f'(FROM "trends-noreply@google.com" SINCE {since_str})'
        )

    ids = data[0].split() if data[0] else []
    if not ids:
        print("[email] No Google Trends newsletters found")
        mail.logout()
        return []

    # Process all found emails, newest first — accumulate across issues
    all_trends: list[dict] = []

    for email_id in reversed(ids):
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0] or not msg_data[0][1]:
            print("[email] Failed to fetch message body, skipping")
            continue
        msg = email_lib.message_from_bytes(msg_data[0][1])
        email_date = msg["Date"] or ""

        # Extract HTML body
        html = None
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode("utf-8", errors="replace")
                break

        if html:
            trends = _parse_newsletter_html(html)
            for t in trends:
                t["email_date"] = email_date
            all_trends.extend(trends)
            print(f"[email] Parsed {len(trends)} trends from newsletter ({email_date})")
        else:
            print("[email] No HTML body found in newsletter")

        if mark_read:
            mail.store(email_id, "+FLAGS", "\\Seen")

    mail.logout()
    return all_trends


# --- Standalone test ---
if __name__ == "__main__":
    trends = fetch_email(mark_read=False)
    print(f"\nExtracted {len(trends)} trends\n")
    for t in trends:
        growth = t["growth"] or "-"
        print(f"  {t['keyword']:<45}  {growth:<18}  [{t['category']}]")
