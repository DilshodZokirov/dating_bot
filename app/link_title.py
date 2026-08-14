"""
Silka orqali sahifa/film nomini aniqlash (faqat metadata).
Fayl yuklab olinmaydi va tarqatilmaydi.

TikTok: oEmbed + sahifa ichidagi desc (ochiq videolar).
Instagram: oEmbed/HTML meta/caption (ochiq postlar; login/yopiqda ishlamasligi mumkin).
"""

from __future__ import annotations

import html as html_lib
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)

# YouTube ba’zan og:title ni juda pastga qo‘yadi
MAX_BYTES = 1_200_000
FETCH_TIMEOUT = 12.0
EARLY_STOP_AFTER = 80_000  # head/meta ko‘pincha shu oralig‘da

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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

GENERIC_TITLE_RE = re.compile(
    r"""^(
        instagram|
        tiktok|
        facebook|
        twitter|
        youtube|
        telegram|
        login\s*[•·\-]\s*instagram|
        instagram\s*[•·\-]\s*login|
        tiktok\s*[•·\-]\s*make\s+your\s+day|
        make\s+your\s+day|
        download\s+tiktok.*
    )$""",
    re.I | re.X,
)

TIKTOK_HOSTS = ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com")
INSTAGRAM_HOSTS = ("instagram.com", "instagr.am")


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = ""
        self.og_title = ""
        self.og_site = ""
        self.og_description = ""
        self.twitter_title = ""
        self.twitter_description = ""

    def handle_starttag(self, tag, attrs):
        attrs_d = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "meta":
            prop = (attrs_d.get("property") or attrs_d.get("name") or "").lower()
            content = attrs_d.get("content") or ""
            if not content:
                return
            if prop == "og:title" and not self.og_title:
                self.og_title = content.strip()
            elif prop == "twitter:title" and not self.twitter_title:
                self.twitter_title = content.strip()
            elif prop == "og:site_name" and not self.og_site:
                self.og_site = content.strip()
            elif prop in ("og:description", "description") and not self.og_description:
                self.og_description = content.strip()
            elif prop == "twitter:description" and not self.twitter_description:
                self.twitter_description = content.strip()

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
    # Instagram: "user on Instagram: \"Caption…\"" → Caption
    m = re.match(
        r'^[^:]+\s+on\s+Instagram:\s*[“"«]?(.*?)[”"»]?\s*$',
        title,
        flags=re.I | re.S,
    )
    if m and m.group(1).strip():
        title = m.group(1).strip()
    title = JUNK_TITLE_PARTS.sub("", title).strip(" -–—|:")
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
    if not title or GENERIC_TITLE_RE.match(title):
        return ""
    return title[:200]


def _host_hint(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return ""


def _host_matches(host: str, suffixes: tuple[str, ...]) -> bool:
    return any(host == h or host.endswith("." + h) for h in suffixes)


def _pick_best_title(*candidates: str) -> str:
    for raw in candidates:
        cleaned = clean_title(raw or "")
        if cleaned:
            return cleaned
    return ""


def _http_headers() -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "uz,ru,en;q=0.9",
        "Referer": "https://www.google.com/",
    }


def _json_unescape(s: str) -> str:
    try:
        return json.loads(f'"{s}"')
    except Exception:
        return html_lib.unescape(s.replace(r"\n", " ").replace(r"\"", '"'))


def _extract_tiktok_desc_from_html(html: str) -> str:
    # 1) rehydration JSON
    m = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        html,
        re.S,
    )
    if m:
        try:
            data = json.loads(m.group(1))
            found: list[str] = []

            def walk(obj):
                if isinstance(obj, dict):
                    # video item structure
                    if "desc" in obj and isinstance(obj["desc"], str) and obj["desc"].strip():
                        # faqat video item atrofida bo‘lsa yaxshiroq
                        if any(k in obj for k in ("id", "video", "author", "stats", "createTime")):
                            found.append(obj["desc"].strip())
                    for v in obj.values():
                        walk(v)
                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)

            walk(data)
            if found:
                return found[0]
        except Exception:
            pass

    # 2) raw "desc":"..."
    for m in re.finditer(r'"desc"\s*:\s*"((?:\\.|[^"\\])*)"', html):
        val = _json_unescape(m.group(1)).strip()
        if val and not GENERIC_TITLE_RE.match(val):
            return val
    return ""


def _extract_instagram_caption_from_html(html: str) -> str:
    # caption text fields commonly embedded in page JSON
    for pat in (
        r'"caption"\s*:\s*\{\s*"text"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"edge_media_to_caption"[^]]*?\"text\"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"accessibility_caption"\s*:\s*"((?:\\.|[^"\\])*)"',
    ):
        m = re.search(pat, html, re.S)
        if m:
            val = _json_unescape(m.group(1)).strip()
            if val and not GENERIC_TITLE_RE.match(val):
                return val
    return ""


async def _fetch_tiktok_oembed(client: httpx.AsyncClient, url: str) -> dict | None:
    try:
        resp = await client.get(
            "https://www.tiktok.com/oembed",
            params={"url": url},
        )
        if resp.status_code != 200:
            return None
        ctype = (resp.headers.get("content-type") or "").lower()
        if "json" not in ctype:
            return None
        data = resp.json()
        title = _pick_best_title(data.get("title") or "")
        if not title:
            return None
        author = (data.get("author_name") or "").strip()
        source = f"TikTok · {author}" if author else "TikTok"
        return {"ok": True, "title": title, "source": source, "error": ""}
    except Exception:
        return None


async def _fetch_instagram_oembed(client: httpx.AsyncClient, url: str) -> dict | None:
    # Ba’zi ochiq postlarda ishlaydi; token talab qilinsa yiqiladi
    endpoints = (
        "https://www.instagram.com/api/v1/oembed/",
        "https://api.instagram.com/oembed",
    )
    for ep in endpoints:
        try:
            resp = await client.get(ep, params={"url": url})
            if resp.status_code != 200:
                continue
            ctype = (resp.headers.get("content-type") or "").lower()
            if "json" not in ctype:
                continue
            data = resp.json()
            title = _pick_best_title(
                data.get("title") or "",
                data.get("author_name") or "",
            )
            if title:
                author = (data.get("author_name") or "").strip()
                source = f"Instagram · {author}" if author else "Instagram"
                return {"ok": True, "title": title, "source": source, "error": ""}
        except Exception:
            continue
    return None


def _meta_content(html: str, *names: str) -> str:
    for name in names:
        # property/name + content (ikkala tartib)
        pats = (
            rf'<meta[^>]+(?:property|name)=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(name)}["\']',
        )
        for pat in pats:
            m = re.search(pat, html, re.I)
            if m and m.group(1).strip():
                return html_lib.unescape(m.group(1).strip())
    return ""


def _html_title_tag(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", html_lib.unescape(m.group(1))).strip()


async def _fetch_html_bytes(client: httpx.AsyncClient, url: str) -> tuple[bytes | None, str, str]:
    """Qaytaradi: (raw_bytes|None, content_type, error)."""
    try:
        async with client.stream("GET", url) as resp:
            if resp.status_code >= 400:
                return None, "", f"http_{resp.status_code}"
            ctype = (resp.headers.get("content-type") or "").lower()
            chunks: list[bytes] = []
            total = 0
            async for chunk in resp.aiter_bytes():
                chunks.append(chunk)
                total += len(chunk)
                if total >= MAX_BYTES:
                    break
                # Erta to‘xtash: og:title allaqachon kelgan bo‘lsa
                if total >= EARLY_STOP_AFTER:
                    probe = b"".join(chunks).decode("utf-8", errors="ignore")
                    if 'property="og:title"' in probe or "property='og:title'" in probe:
                        break
            return b"".join(chunks), ctype, ""
    except Exception as e:
        return None, "", type(e).__name__


async def _fetch_html_meta(client: httpx.AsyncClient, url: str, host: str) -> dict:
    raw, ctype, err = await _fetch_html_bytes(client, url)
    if raw is None:
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": err or "fetch_failed",
        }
    if ctype and "text/html" not in ctype and "application/xhtml" not in ctype:
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": "not_html",
        }

    text = raw.decode("utf-8", errors="ignore")
    parser = _MetaParser()
    try:
        parser.feed(text)
    except Exception:
        pass

    # Regex — HTMLParser ba’zan katta/noto‘g‘ri sahifalarda yiqiladi
    og_title = parser.og_title or _meta_content(text, "og:title")
    tw_title = parser.twitter_title or _meta_content(text, "twitter:title")
    og_desc = parser.og_description or _meta_content(text, "og:description", "description")
    tw_desc = parser.twitter_description or _meta_content(text, "twitter:description")
    page_title = parser.title.strip() or _html_title_tag(text)
    og_site = parser.og_site or _meta_content(text, "og:site_name")

    embedded = ""
    if _host_matches(host, TIKTOK_HOSTS):
        embedded = _extract_tiktok_desc_from_html(text)
    elif _host_matches(host, INSTAGRAM_HOSTS):
        embedded = _extract_instagram_caption_from_html(text)

    title = _pick_best_title(
        embedded,
        og_title,
        tw_title,
        og_desc,
        tw_desc,
        page_title,
    )
    if not title:
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": "no_title",
        }

    if _host_matches(host, INSTAGRAM_HOSTS):
        source = "Instagram"
    elif _host_matches(host, TIKTOK_HOSTS):
        source = "TikTok"
    else:
        source = og_site or host or "link"

    return {
        "ok": True,
        "title": title,
        "source": source,
        "host": host,
        "error": "",
    }


async def fetch_page_title(url: str) -> dict:
    """
    Qaytaradi: {ok, title, source, host, error}
    """
    host = _host_hint(url)
    headers = _http_headers()

    try:
        async with httpx.AsyncClient(
            timeout=FETCH_TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:
            if _host_matches(host, TIKTOK_HOSTS):
                oembed = await _fetch_tiktok_oembed(client, url)
                if oembed and oembed.get("ok"):
                    oembed["host"] = host
                    return oembed
                result = await _fetch_html_meta(client, url, host)
                return result

            if _host_matches(host, INSTAGRAM_HOSTS):
                oembed = await _fetch_instagram_oembed(client, url)
                if oembed and oembed.get("ok"):
                    oembed["host"] = host
                    return oembed
                result = await _fetch_html_meta(client, url, host)
                return result

            return await _fetch_html_meta(client, url, host)
    except Exception as e:
        return {
            "ok": False,
            "title": "",
            "source": "",
            "host": host,
            "error": type(e).__name__,
        }


async def resolve_movie_title_from_message(message) -> dict:
    urls = extract_urls_from_message(message)
    if not urls:
        return {"ok": False, "error": "no_url", "title": "", "url": ""}
    url = urls[0]
    result = await fetch_page_title(url)
    result["url"] = url
    return result
