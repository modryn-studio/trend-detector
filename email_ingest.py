"""
email_ingest.py — Google Trends newsletter parser (Source 3)

Connects to Gmail via IMAP, fetches unread Google Trends Daily Trending
newsletters, parses the narrative HTML to extract:
  - Trend keywords (quoted phrases)
  - Growth percentages (+290%, breakout, all-time high)
  - Category/section names (from h3/h4 headings)

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


def _parse_newsletter_html(html: str) -> list[dict]:
    """Parse one newsletter's HTML into a list of trend dicts."""
    soup = BeautifulSoup(html, "html.parser")
    trends: list[dict] = []
    seen_keywords: set[str] = set()

    # Find section headers — newsletters use h3 or h4
    sections = soup.find_all(["h3", "h4"])

    if not sections:
        # Fallback: try to extract from the full body text
        full_text = soup.get_text(" ", strip=True)
        _extract_from_text(full_text, "general", trends, seen_keywords)
        return trends

    for sec in sections:
        category = sec.get_text(strip=True)
        if category.lower() in _SKIP_SECTIONS:
            continue

        # Collect text from siblings until the next heading
        text_parts: list[str] = []
        for sib in sec.find_next_siblings():
            if sib.name in ("h3", "h4"):
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
