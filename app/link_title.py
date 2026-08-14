"""
Silka orqali sahifa/film nomini aniqlash (faqat metadata).
Fayl yuklab olinmaydi va tarqatilmaydi.
"""

from __future__ import annotations

import html as html_lib
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)

# Juda katta HTML kerak emas — title odatda boshida
MAX_BYTES = 200_000
FETCH_TIMEOUT = 8.0

USER_AGENT = (
    "Mozilla/5.0 (compatible; SoylaBot/1.0; +https://t.me/soylaibot) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

JUNK_TITLE_PARTS = re.compile(
    r"""
    \s*[\|\-–—:]\s*(
        YouTube|Instagram|TikTok|Facebook|Twitter|X|Telegram|
        Watch\s+Online|Online\s+Watch|Free\s+Download|
        Кинопоиск|IMDb|Letterboxd|
        Home|Главная|Asosiy
    ).*$
    """,
    re.I | re.X,
)


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = ""
        self.og_title = ""
        self.og_site = ""
        self.twitter_title = ""

    def handle_starttag(self, tag, attrs):
        attrs_d = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "meta":
            prop = (attrs_d.get("property") or attrs_d.get("name") or "").lower()
            content = attrs_d.get("content") or ""
            if prop == "og:title" and content and not self.og_title:
                self.og_title = content.strip()
            elif prop == "twitter:title" and content and not self.twitter_title:
                self.twitter_title = content.strip()
            elif prop == "og:site_name" and content and not self.og_site:
                self.og_site = content.strip()

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def extract_urls_from_text(text: str) -> list[str]:
    if not text:
        return []
    found = []
    for m in URL_RE.finditer(text):
        u = m.group(0).rstrip(").,]}>\"'")
        if u not in found:
            found.append(u)
    return found


def extract_urls_from_message(message) -> list[str]:
    text = message.text or message.caption or ""
    urls: list[str] = []
    entities = list(message.entities or []) + list(message.caption_entities or [])
    for e in entities:
        et = getattr(e, "type", None)
        et_val = et.value if hasattr(et, "value") else str(et)
        if et_val == "url":
            chunk = text[e.offset : e.offset + e.length]
            if chunk and chunk not in urls:
                urls.append(chunk.rstrip(").,]}>\"'"))
        elif et_val == "text_link" and getattr(e, "url", None):
            if e.url not in urls:
                urls.append(e.url)
    for u in extract_urls_from_text(text):
        if u not in urls:
            urls.append(u)
    return urls


def clean_title(raw: str) -> str:
    if not raw:
        return ""
    title = html_lib.unescape(raw).strip()
    title = re.sub(r"\s+", " ", title)
    title = JUNK_TITLE_PARTS.sub("", title).strip(" -–—|:")
    # "Watch Foo Bar (2021) full movie" → "Foo Bar (2021)"
    title = re.sub(
        r"^(watch|stream|download|смотреть|онлайн)\s+",
        "",
        title,
        flags=re.I,
    ).strip()
    title = re.sub(
        r"\s+(full\s+movie|free\s+online|hd|camrip|web-?dl).*$",
        "",
        title,
        flags=re.I,
    ).strip(" -–—|:")
    return title[:200]


def _host_hint(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


async def fetch_page_title(url: str) -> dict:
    """
    Qaytaradi: {ok, title, source, host, error}
    """
    host = _host_hint(url)
    # Telegram/Instagram sahifalari ko‘pincha ochilmaydi yoki login talab qiladi
    hard = ("instagram.com", "instagr.am", "tiktok.com", "vm.tiktok.com")
    if any(host.endswith(h) or host == h for h in hard):
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": "blocked_host",
        }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "uz,ru,en;q=0.8",
    }
    try:
        async with httpx.AsyncClient(
            timeout=FETCH_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code >= 400:
                    return {
                        "ok": False,
                        "title": "",
                        "source": "",
                        "host": host,
                        "error": f"http_{resp.status_code}",
                    }
                ctype = (resp.headers.get("content-type") or "").lower()
                if "text/html" not in ctype and "application/xhtml" not in ctype and ctype:
                    # To‘g‘ridan-to‘g‘ri video/fayl — nom yo‘q
                    return {
                        "ok": False,
                        "title": "",
                        "source": "",
                        "host": host,
                        "error": "not_html",
                    }
                chunks: list[bytes] = []
                total = 0
                async for chunk in resp.aiter_bytes():
                    chunks.append(chunk)
                    total += len(chunk)
                    if total >= MAX_BYTES:
                        break
                raw = b"".join(chunks)
    except Exception as e:
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": type(e).__name__,
        }

    # Encoding
    text = raw.decode("utf-8", errors="ignore")
    parser = _MetaParser()
    try:
        parser.feed(text)
    except Exception:
        pass

    raw_title = parser.og_title or parser.twitter_title or parser.title
    title = clean_title(raw_title)
    if not title:
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": "no_title",
        }

    source = parser.og_site or host or "link"
    return {
        "ok": True,
        "title": title,
        "source": source,
        "host": host,
        "error": "",
    }


async def resolve_movie_title_from_message(message) -> dict:
    urls = extract_urls_from_message(message)
    if not urls:
        return {"ok": False, "error": "no_url", "title": "", "url": ""}
    # Birinchi silka — odatda asosiy
    url = urls[0]
    result = await fetch_page_title(url)
    result["url"] = url
    return result
