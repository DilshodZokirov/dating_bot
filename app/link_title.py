"""
Silka orqali film nomini internetdan aniqlash.

Yo‘l:
1) Silkadagi post/sahifadan preview rasm (thumbnail / og:image) olinadi
2) Rasm bo‘yicha internet reverse-image qidiruv (Yandex CBIR)
3) Natijadan film nomi ajratiladi

Caption matni JAVOB sifatida qaytarilmaydi.
Video/fayl yuklab olinmaydi va foydalanuvchiga yuborilmaydi.
"""

from __future__ import annotations

import html as html_lib
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)

MAX_BYTES = 1_200_000
FETCH_TIMEOUT = 15.0
EARLY_STOP_AFTER = 80_000

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

TIKTOK_HOSTS = ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com")
INSTAGRAM_HOSTS = ("instagram.com", "instagr.am")
SOCIAL_HOSTS = TIKTOK_HOSTS + INSTAGRAM_HOSTS

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
        instagram|tiktok|facebook|twitter|youtube|telegram|
        login\s*[•·\-]\s*instagram|instagram\s*[•·\-]\s*login|
        tiktok\s*[•·\-]\s*make\s+your\s+day|make\s+your\s+day|
        download\s+tiktok.*
    )$""",
    re.I | re.X,
)

YEAR_IN_TEXT_RE = re.compile(r"(?:19|20)\d{2}")


class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = ""
        self.og_title = ""
        self.og_site = ""
        self.og_image = ""
        self.og_description = ""
        self.twitter_title = ""
        self.twitter_image = ""

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
            elif prop in ("og:image", "og:image:secure_url") and not self.og_image:
                self.og_image = content.strip()
            elif prop in ("twitter:image", "twitter:image:src") and not self.twitter_image:
                self.twitter_image = content.strip()
            elif prop in ("og:description", "description") and not self.og_description:
                self.og_description = content.strip()

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


def normalize_media_url(url: str) -> str:
    """Instagram/TikTok tracking parametrlarini olib tashlash."""
    if not url:
        return url
    try:
        p = urlparse(url.strip())
        host = (p.netloc or "").lower()
        if "instagram.com" in host or "instagr.am" in host or "tiktok.com" in host:
            # path ni saqlab, ?igsh=... ni olib tashlaymiz
            return f"{p.scheme}://{p.netloc}{p.path}"
    except Exception:
        pass
    return url


def _host_matches(host: str, suffixes: tuple[str, ...]) -> bool:
    return any(host == h or host.endswith("." + h) for h in suffixes)


def _http_headers() -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "uz,ru,en;q=0.9",
        "Referer": "https://www.google.com/",
    }


def _meta_content(html: str, *names: str) -> str:
    for name in names:
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


def normalize_movie_hit(title: str = "", subtitle: str = "") -> str:
    """
    Yandex CBIR: title='Начало', subtitle='Inception, 2010 (18+)'
    → 'Inception (2010)'
    """
    subtitle = html_lib.unescape(subtitle or "").strip()
    title = html_lib.unescape(title or "").strip()

    # Subtitle ko‘pincha: "Inception, 2010 (18+)" yoki "Movie Name (2010)"
    if subtitle:
        # English/original name + year
        m = re.match(
            r"^\s*(?P<name>.+?)(?:,\s*|\s+)(?P<year>(?:19|20)\d{2})\b",
            subtitle,
        )
        if m:
            name = clean_title(m.group("name"))
            if name:
                return f"{name} ({m.group('year')})"
        # Faqat "Name (2010)"
        m = re.match(
            r"^\s*(?P<name>.+?)\s*\((?P<year>(?:19|20)\d{2})\)",
            subtitle,
        )
        if m:
            name = clean_title(m.group("name"))
            if name:
                return f"{name} ({m.group('year')})"
        cleaned = clean_title(re.sub(r"\s*\(\d{1,2}\+\)\s*$", "", subtitle))
        if cleaned and not looks_like_prose(cleaned):
            return cleaned

    cleaned = clean_title(title)
    if cleaned and not looks_like_prose(cleaned):
        return cleaned
    return ""


def looks_like_prose(text: str) -> bool:
    if not text:
        return False
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) >= 100:
        return True
    if t.count(".") + t.count("!") + t.count("?") >= 2:
        return True
    if re.match(
        r"^(tonight|today|yesterday|this\s+(week|weekend)|just|when|after|"
        r"known\s+for|check\s+out|swipe|link\s+in)\b",
        t,
        re.I,
    ):
        return True
    if t.count(",") >= 3 and len(t) > 70:
        return True
    return False


def parse_yandex_cbir_hits(html: str) -> list[dict]:
    """Yandex Images reverse-search HTML dan film entitylarini ajratish."""
    if not html:
        return []
    # Ba’zi javoblar HTML-escape qilingan JSON bo‘laklari
    unescaped = html_lib.unescape(html)
    hits: list[dict] = []

    # objectResponses ichidagi title/subtitle juftlari
    for m in re.finditer(
        r'"title"\s*:\s*"(?P<title>(?:\\.|[^"\\])*)"\s*,\s*"subtitle"\s*:\s*"(?P<sub>(?:\\.|[^"\\])*)"',
        unescaped,
    ):
        try:
            title = json.loads(f'"{m.group("title")}"')
            sub = json.loads(f'"{m.group("sub")}"')
        except Exception:
            title = m.group("title")
            sub = m.group("sub")
        movie = normalize_movie_hit(title, sub)
        if movie:
            hits.append({"title": movie, "raw_title": title, "raw_subtitle": sub})

    # Escape qolgan variant: &quot;subtitle&quot;:&quot;...&quot;
    if not hits:
        for m in re.finditer(
            r'&quot;title&quot;:&quot;(?P<title>[^&]{1,120})&quot;,&quot;subtitle&quot;:&quot;(?P<sub>[^&]{1,160})&quot;',
            html,
        ):
            movie = normalize_movie_hit(m.group("title"), m.group("sub"))
            if movie:
                hits.append(
                    {
                        "title": movie,
                        "raw_title": m.group("title"),
                        "raw_subtitle": m.group("sub"),
                    }
                )

    # Dedup
    seen: set[str] = set()
    out: list[dict] = []
    for h in hits:
        key = h["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


async def _fetch_html_bytes(client: httpx.AsyncClient, url: str) -> tuple[bytes | None, str, str]:
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
                if total >= EARLY_STOP_AFTER:
                    probe = b"".join(chunks).decode("utf-8", errors="ignore")
                    if 'property="og:image"' in probe or "property='og:image'" in probe:
                        # Image topildi — biroz ko‘proq o‘qib title ham olish mumkin
                        if total >= 200_000 or 'property="og:title"' in probe:
                            break
            return b"".join(chunks), ctype, ""
    except Exception as e:
        return None, "", type(e).__name__


async def _oembed_thumbnail(client: httpx.AsyncClient, url: str, host: str) -> dict:
    """
    Social oEmbed — faqat thumbnail_url / provider.
    title (caption) JAVOB emas, e’tiborsiz qoldiriladi.
    """
    endpoints: list[str] = []
    if _host_matches(host, TIKTOK_HOSTS):
        endpoints = ["https://www.tiktok.com/oembed"]
    elif _host_matches(host, INSTAGRAM_HOSTS):
        endpoints = [
            "https://www.instagram.com/api/v1/oembed/",
            "https://api.instagram.com/oembed",
        ]
    for ep in endpoints:
        try:
            resp = await client.get(ep, params={"url": url})
            if resp.status_code != 200:
                continue
            ctype = (resp.headers.get("content-type") or "").lower()
            if "json" not in ctype:
                continue
            data = resp.json()
            thumb = (data.get("thumbnail_url") or "").strip()
            if thumb:
                return {
                    "thumbnail_url": thumb,
                    "provider": data.get("provider_name") or host,
                    "author": (data.get("author_name") or "").strip(),
                }
        except Exception:
            continue
    return {}


async def _page_preview(client: httpx.AsyncClient, url: str, host: str) -> dict:
    """Sahifadan preview rasm + (ixtiyoriy) oddiy page title."""
    raw, ctype, err = await _fetch_html_bytes(client, url)
    if raw is None:
        return {"error": err or "fetch_failed", "thumbnail_url": "", "page_title": ""}
    if ctype and "text/html" not in ctype and "application/xhtml" not in ctype:
        return {"error": "not_html", "thumbnail_url": "", "page_title": ""}

    text = raw.decode("utf-8", errors="ignore")
    parser = _MetaParser()
    try:
        parser.feed(text)
    except Exception:
        pass

    thumb = (
        parser.og_image
        or parser.twitter_image
        or _meta_content(text, "og:image", "og:image:secure_url", "twitter:image")
    )
    page_title = clean_title(
        parser.og_title
        or parser.twitter_title
        or parser.title
        or _html_title_tag(text)
        or _meta_content(text, "og:title", "twitter:title")
    )
    return {
        "error": "",
        "thumbnail_url": thumb,
        "page_title": page_title,
        "site": parser.og_site or host,
    }


async def _download_image(
    client: httpx.AsyncClient, image_url: str
) -> tuple[bytes | None, str]:
    """Preview rasmni o‘zimiz yuklab olamiz (Yandex IG CDN ni ocholmasligi mumkin)."""
    try:
        resp = await client.get(image_url)
        if resp.status_code >= 400 or not resp.content:
            return None, ""
        ctype = (resp.headers.get("content-type") or "image/jpeg").split(";")[0].strip()
        if not ctype.startswith("image/"):
            if ctype not in ("application/octet-stream", ""):
                return None, ""
            ctype = "image/jpeg"
        data = resp.content[:2_500_000]
        if len(data) < 500:
            return None, ""
        return data, ctype or "image/jpeg"
    except Exception:
        return None, ""


def _gemini_api_key() -> str:
    import os

    api_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if api_key:
        return api_key
    try:
        from app.config import settings

        return (getattr(settings, "gemini_api_key", "") or "").strip()
    except Exception:
        return ""


async def yandex_reverse_image_movie(
    client: httpx.AsyncClient,
    *,
    image_url: str = "",
    image_bytes: bytes | None = None,
    mime: str = "image/jpeg",
) -> dict | None:
    """
    Yandex Images CBIR.
    Avval fayl upload (Instagram CDN uchun), keyin URL usuli.
    """
    try:
        html = ""
        if image_bytes:
            files = {"upfile": ("frame.jpg", image_bytes, mime or "image/jpeg")}
            resp = await client.post(
                "https://yandex.com/images/search",
                params={"rpt": "imageview"},
                files=files,
            )
            if resp.status_code == 200:
                html = resp.text
        if (not html or not parse_yandex_cbir_hits(html)) and image_url:
            resp = await client.get(
                "https://yandex.com/images/search",
                params={"rpt": "imageview", "url": image_url},
            )
            if resp.status_code == 200:
                html = resp.text
        if not html:
            return None
        hits = parse_yandex_cbir_hits(html)
        if not hits:
            return None
        best = next((h for h in hits if YEAR_IN_TEXT_RE.search(h["title"])), hits[0])
        return {
            "ok": True,
            "title": best["title"],
            "source": "Internet · Yandex Images",
            "error": "",
        }
    except Exception:
        return None


async def gemini_identify_movie(
    *,
    image_url: str = "",
    image_bytes: bytes | None = None,
    mime: str = "image/jpeg",
) -> dict | None:
    """GEMINI_API_KEY bo‘lsa — kadrni AI bilan tanish (Instagram/TikTok uchun asosiy)."""
    import base64

    api_key = _gemini_api_key()
    if not api_key:
        return None

    prompt = (
        "Identify the movie or TV show shown in this image/video frame. "
        "Ignore fashion captions, watermarks, usernames, and UI chrome. "
        "Reply with ONLY the official title and year like: Inception (2010). "
        "If you cannot identify it, reply exactly: UNKNOWN"
    )
    models = (
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-flash-latest",
    )
    try:
        async with httpx.AsyncClient(timeout=30, headers=_http_headers()) as client:
            data = image_bytes
            ctype = mime or "image/jpeg"
            if data is None and image_url:
                data, ctype = await _download_image(client, image_url)
            if not data:
                return None
            b64 = base64.b64encode(data[:2_000_000]).decode("ascii")
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": ctype, "data": b64}},
                        ]
                    }
                ]
            }
            for model in models:
                endpoint = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model}:generateContent?key={api_key}"
                )
                resp = await client.post(endpoint, json=payload)
                if resp.status_code != 200:
                    continue
                body = resp.json()
                text_out = (
                    body.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                    .strip()
                )
                if not text_out or text_out.upper().startswith("UNKNOWN"):
                    continue
                line = text_out.splitlines()[0].strip().strip("`\"'")
                movie = normalize_movie_hit(line, line) or clean_title(line)
                if movie and not looks_like_prose(movie):
                    return {
                        "ok": True,
                        "title": movie,
                        "source": f"Internet · Gemini ({model})",
                        "error": "",
                    }
    except Exception:
        return None
    return None


async def identify_movie_from_image_bytes(
    image_bytes: bytes, mime: str = "image/jpeg"
) -> dict:
    """Telegram orqali yuborilgan screenshot/rasmni aniqlash."""
    if not image_bytes:
        return {"ok": False, "title": "", "source": "", "error": "no_image"}
    if not _gemini_api_key():
        return {"ok": False, "title": "", "source": "", "error": "need_gemini"}

    ghit = await gemini_identify_movie(image_bytes=image_bytes, mime=mime)
    if ghit and ghit.get("ok"):
        return ghit

    try:
        async with httpx.AsyncClient(
            timeout=FETCH_TIMEOUT, follow_redirects=True, headers=_http_headers()
        ) as client:
            hit = await yandex_reverse_image_movie(
                client, image_bytes=image_bytes, mime=mime
            )
            if hit and hit.get("ok"):
                return hit
    except Exception:
        pass
    return {"ok": False, "title": "", "source": "", "error": "not_identified"}


async def fetch_page_title(url: str) -> dict:
    """
    Asosiy API: {ok, title, source, host, error}
    Caption emas — preview kadr + internet/AI.
    """
    url = normalize_media_url(url)
    host = _host_hint(url)
    social = _host_matches(host, SOCIAL_HOSTS)

    try:
        async with httpx.AsyncClient(
            timeout=FETCH_TIMEOUT,
            follow_redirects=True,
            headers=_http_headers(),
        ) as client:
            thumb = ""
            page_title = ""
            site = host

            if social:
                oe = await _oembed_thumbnail(client, url, host)
                thumb = oe.get("thumbnail_url") or ""
                if oe.get("provider"):
                    site = oe["provider"]

            if not thumb:
                preview = await _page_preview(client, url, host)
                thumb = preview.get("thumbnail_url") or ""
                page_title = preview.get("page_title") or ""
                site = preview.get("site") or site
            elif not social:
                preview = await _page_preview(client, url, host)
                page_title = preview.get("page_title") or page_title

            img_bytes: bytes | None = None
            mime = "image/jpeg"
            if thumb:
                img_bytes, mime = await _download_image(client, thumb)

            if social and thumb:
                if _gemini_api_key():
                    ghit = await gemini_identify_movie(
                        image_url=thumb, image_bytes=img_bytes, mime=mime
                    )
                    if ghit and ghit.get("ok"):
                        ghit["host"] = host
                        return ghit

                hit = await yandex_reverse_image_movie(
                    client, image_url=thumb, image_bytes=img_bytes, mime=mime
                )
                if hit and hit.get("ok"):
                    hit["host"] = host
                    return hit

                if not _gemini_api_key():
                    return {
                        "ok": False,
                        "title": "",
                        "source": "",
                        "host": host,
                        "error": "need_gemini",
                    }
                return {
                    "ok": False,
                    "title": "",
                    "source": "",
                    "host": host,
                    "error": "not_identified",
                }

            if thumb:
                hit = await yandex_reverse_image_movie(
                    client, image_url=thumb, image_bytes=img_bytes, mime=mime
                )
                if hit and hit.get("ok"):
                    hit["host"] = host
                    return hit
                ghit = await gemini_identify_movie(
                    image_url=thumb, image_bytes=img_bytes, mime=mime
                )
                if ghit and ghit.get("ok"):
                    ghit["host"] = host
                    return ghit

            if not social and page_title and not looks_like_prose(page_title):
                if YEAR_IN_TEXT_RE.search(page_title) or len(page_title) <= 80:
                    return {
                        "ok": True,
                        "title": page_title,
                        "source": site or host or "link",
                        "host": host,
                        "error": "",
                    }

            return {
                "ok": False,
                "title": "",
                "source": "",
                "host": host,
                "error": "no_image" if not thumb else "not_identified",
            }
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
