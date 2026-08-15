"""
Silka orqali film nomini internetdan aniqlash.

Yo‘l:
1) Silkadagi post/sahifadan preview rasm (thumbnail / og:image) olinadi
2) Rasm bo‘yicha internet reverse-image qidiruv (Yandex CBIR) yoki Gemini
3) Nom app UI tiliga moslab chiqariladi + qisqa mazmun

Caption matni JAVOB sifatida qaytarilmaydi.
Video/fayl yuklab olinmaydi va foydalanuvchiga yuborilmaydi.
"""

from __future__ import annotations

import html as html_lib
import json
import re
from collections.abc import Awaitable, Callable
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

# progress step keys → i18n: link_progress_{step}
ProgressCb = Callable[[str], Awaitable[None]]

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


def _title_years(text: str) -> set[str]:
    return set(YEAR_IN_TEXT_RE.findall(text or ""))


def _title_tokens(text: str) -> set[str]:
    s = YEAR_IN_TEXT_RE.sub(" ", text or "")
    s = re.sub(r"[^\w\s]", " ", s, flags=re.U)
    return {t.lower() for t in s.split() if len(t) > 1}


def _script_bucket(text: str) -> str:
    if re.search(r"[\u0400-\u04FF]", text or ""):
        return "cyr"
    if re.search(r"[A-Za-z]", text or ""):
        return "lat"
    if re.search(r"[\u0600-\u06FF]", text or ""):
        return "ar"
    if re.search(r"[\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]", text or ""):
        return "cjk"
    return "other"


def titles_same_movie(original: str, candidate: str) -> bool:
    """
    Lokalizatsiya boshqa filmga almashtirmasin.
    Yil zid kelasa — boshqa film. Tokenlar juda farq qilsa — rad.
    Turli yozuv (lotin/kirill) + bir xil yil — ruxsat (tarjima).
    """
    a = (original or "").strip()
    b = (candidate or "").strip()
    if not a or not b:
        return False
    if a.lower() == b.lower():
        return True
    ya, yb = _title_years(a), _title_years(b)
    if ya and yb and ya.isdisjoint(yb):
        return False
    ta, tb = _title_tokens(a), _title_tokens(b)
    if ta and tb:
        inter = ta & tb
        if inter:
            ratio = len(inter) / min(len(ta), len(tb))
            if ratio >= 0.4 or len(inter) >= 2:
                return True
            # Bitta uzun umumiy so‘z (masalan Inception)
            if any(len(x) >= 5 for x in inter):
                return True
    # Cross-script localization with matching year (Inception ↔ Начало)
    if ya and yb and ya == yb and _script_bucket(a) != _script_bucket(b):
        return True
    # Cross-script without year: faqat qisqa o‘zgarish emas — ishonchsiz
    if not ya and not yb and _script_bucket(a) != _script_bucket(b):
        # Length similar → ehtimol tarjima
        if abs(len(a) - len(b)) <= max(8, len(a) // 2):
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


# App UI language → human label for Gemini prompts
LANG_LABELS: dict[str, str] = {
    "uz": "Uzbek (Latin script, o'zbekcha)",
    "ru": "Russian",
    "en": "English",
    "de": "German",
    "tg": "Tajik",
    "tr": "Turkish",
    "ko": "Korean",
    "ja": "Japanese",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
}

_GEMINI_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
)


def _lang_label(lang: str) -> str:
    return LANG_LABELS.get((lang or "uz").lower(), "English")


def _parse_gemini_movie_json(text_out: str) -> dict | None:
    """Gemini javobidan {found, title, summary, title_raw?} JSON ajratish."""
    if not text_out:
        return None
    raw = text_out.strip()
    # ```json ... ``` ni olib tashlash
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw, re.I)
    if fence:
        raw = fence.group(1).strip()
    # Birinchi {...} blok
    brace = re.search(r"\{[\s\S]*\}", raw)
    if not brace:
        return None
    try:
        data = json.loads(brace.group(0))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    if data.get("found") is False:
        return {"found": False}
    title = clean_title(str(data.get("title") or "").strip())
    title_raw = clean_title(
        str(data.get("title_raw") or data.get("on_screen_title") or "").strip()
    )
    if not title and title_raw:
        title = title_raw
    if not title or looks_like_prose(title):
        return None
    summary = str(data.get("summary") or "").strip()
    # HTML/markdown tozalash
    summary = re.sub(r"[`*_#]+", "", summary)
    summary = re.sub(r"\s+", " ", summary).strip()
    if len(summary) > 600:
        summary = summary[:597].rstrip() + "…"
    out = {"found": True, "title": title, "summary": summary}
    if title_raw:
        out["title_raw"] = title_raw
    return out


async def _gemini_generate_text(
    client: httpx.AsyncClient,
    api_key: str,
    parts: list[dict],
) -> tuple[str, str]:
    """Birinchi ishlagan modeldan matn qaytaradi: (text, model)."""
    headers = {**_http_headers(), "x-goog-api-key": api_key}
    last_errors: list[str] = []
    for model in _GEMINI_MODELS:
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )
        resp = await client.post(
            endpoint,
            json={"contents": [{"parts": parts}]},
            headers=headers,
        )
        if resp.status_code != 200:
            last_errors.append(f"{model}:{resp.status_code}")
            continue
        body = resp.json()
        text_out = (
            body.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        if text_out:
            return text_out, model
    if last_errors:
        print(f"gemini generate failed: {last_errors[:8]}", flush=True)
    return "", ""


async def gemini_enrich_movie(title: str, lang: str = "uz") -> dict | None:
    """
    Topilgan nomni app tiliga o‘girish + qisqa mazmun (spoiler-light).
    MUHIM: boshqa filmga almashtirmaydi — input title = film identifikatori.
    """
    title = (title or "").strip()
    if not title:
        return None
    api_key = _gemini_api_key()
    if not api_key:
        return {"ok": True, "title": title, "summary": "", "source": "title"}

    lang_name = _lang_label(lang)
    prompt = (
        f"LOCKED movie identity (do NOT change to another film): {title!r}\n"
        f"App UI language: {lang_name} (code: {lang}).\n\n"
        "Return ONLY valid JSON (no markdown):\n"
        '{"found":true,"title":"...","summary":"..."}\n'
        "Rules:\n"
        "- You must keep the SAME movie as the locked identity.\n"
        f"- title: official/local name of THAT same movie in {lang_name}, "
        "with the same year if the input has a year. "
        "If you do not know a local title, repeat the input title EXACTLY.\n"
        "- NEVER substitute a different / similar / more famous film.\n"
        f"- summary: 2-3 short sentences in {lang_name} about THIS film only "
        "(spoiler-light, max ~400 chars).\n"
        "If the input is not a real movie: {\"found\":false}"
    )
    try:
        async with httpx.AsyncClient(timeout=45, headers=_http_headers()) as client:
            text_out, model = await _gemini_generate_text(
                client, api_key, [{"text": prompt}]
            )
        parsed = _parse_gemini_movie_json(text_out)
        if parsed and parsed.get("found") and parsed.get("title"):
            new_title = parsed["title"]
            # Boshqa filmga o‘tib ketgan bo‘lsa — asl nomni saqlaymiz
            if not titles_same_movie(title, new_title):
                print(
                    f"gemini_enrich_movie reject swap: {title!r} -> {new_title!r}",
                    flush=True,
                )
                new_title = title
            return {
                "ok": True,
                "title": new_title,
                "summary": parsed.get("summary") or "",
                "source": f"Internet · Gemini enrich ({model})",
                "error": "",
            }
    except Exception as e:
        print(f"gemini_enrich_movie error: {type(e).__name__}: {e}", flush=True)
    return {"ok": True, "title": title, "summary": "", "source": "title", "error": ""}


async def _progress(on_progress: ProgressCb | None, step: str) -> None:
    """Foydalanuvchiga jarayon bosqichini ko‘rsatish (best-effort)."""
    if not on_progress:
        return
    try:
        await on_progress(step)
    except Exception:
        pass


async def ensure_localized_result(
    result: dict, lang: str = "uz", on_progress: ProgressCb | None = None
) -> dict:
    """Natijaga tilga mos nom + summary qo‘shish (yo‘q bo‘lsa Gemini)."""
    if not result or not result.get("ok") or not result.get("title"):
        out = dict(result or {})
        out.setdefault("summary", "")
        return out
    out = dict(result)
    out.setdefault("summary", "")
    original_title = out["title"]
    # Vision JSON allaqachon til + mazmun bergan — lekin nomni ham tekshiramiz
    if out.get("localized") is True and out.get("summary"):
        # title_raw saqlangan bo‘lsa — u asosiy haqiqat
        raw = (out.get("title_raw") or "").strip()
        if raw and not titles_same_movie(raw, out["title"]):
            print(
                f"ensure_localized reject vision swap: {raw!r} -> {out['title']!r}",
                flush=True,
            )
            out["title"] = raw
        return out
    await _progress(on_progress, "localize")
    enriched = await gemini_enrich_movie(original_title, lang)
    if enriched and enriched.get("ok"):
        cand = enriched.get("title") or original_title
        if titles_same_movie(original_title, cand):
            out["title"] = cand
        else:
            out["title"] = original_title
            print(
                f"ensure_localized keep original: {original_title!r} (rejected {cand!r})",
                flush=True,
            )
        if enriched.get("summary"):
            out["summary"] = enriched["summary"]
        out["localized"] = True
    return out


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


def extract_movie_from_ocr_text(text: str) -> str:
    """
    Screenshot/caption matnidan film nomini ajratish.
    Masalan: "Osmondan tushgan fil 2023 — o'zbekcha nom"
    """
    if not text:
        return ""
    raw = html_lib.unescape(text)
    raw = raw.replace("\u2014", "-").replace("\u2013", "-")

    # 1) Aniq: Title (2010) yoki Title 2010
    patterns = [
        re.compile(
            r"(?P<title>[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳІіЇїЄєĞğÜüŞşÖöÇç0-9][^.\n|]{1,80}?)"
            r"\s*[\(\[]?(?P<year>(?:19|20)\d{2})[\)\]]?",
            re.U,
        ),
    ]
    for pat in patterns:
        for m in pat.finditer(raw):
            title = clean_title(m.group("title"))
            year = m.group("year")
            if not title or looks_like_prose(title):
                continue
            # Spam/kod satrlarini rad et
            low = title.lower()
            if any(
                x in low
                for x in (
                    "multfilm kodi",
                    "kod:",
                    "instagram",
                    "reels",
                    "friends",
                    "subscribe",
                    "obuna",
                )
            ):
                continue
            if len(title) < 3 or len(title) > 80:
                continue
            if title.count(",") >= 2:
                continue
            return f"{title} ({year})"

    # 2) "Kino: ..." / "Film: ..."
    for m in re.finditer(
        r"(?im)^\s*(?:film|movie|kino|multfilm|название|nom)\s*[:\-]\s*(.+?)\s*$",
        raw,
    ):
        cand = clean_title(m.group(1))
        if cand and not looks_like_prose(cand) and len(cand) <= 80:
            return cand

    return ""


async def gemini_identify_movie(
    *,
    image_url: str = "",
    image_bytes: bytes | None = None,
    mime: str = "image/jpeg",
    lang: str = "uz",
) -> dict | None:
    """GEMINI_API_KEY — rasm/kadrni tanish; nom + qisqa mazmun app tilida."""
    import base64

    api_key = _gemini_api_key()
    if not api_key:
        return None

    lang_name = _lang_label(lang)
    # Avval ekrandagi aniq matn — taxminiy boshqa filmga o‘tmasin
    plain_prompts = (
        (
            "This is a screenshot that may include Instagram/TikTok UI and captions. "
            "Read ALL visible text. If a movie/cartoon title with year appears, "
            "reply with ONLY that title and year EXACTLY as shown "
            "(example: Osmondan tushgan fil (2023)). "
            "Do not translate. Do not guess another film. "
            "If none, reply exactly: UNKNOWN"
        ),
        (
            "If you can visually identify the movie (no clear title text), "
            "reply ONLY: Title (Year). Otherwise: UNKNOWN"
        ),
    )
    json_prompt = (
        "This is a screenshot/frame that may include Instagram/TikTok UI.\n"
        "Identify the movie or animated film.\n"
        f"App UI language: {lang_name} (code: {lang}).\n\n"
        "Return ONLY valid JSON (no markdown):\n"
        '{"found":true,"title_raw":"...","title":"...","summary":"...",'
        '"confidence":"high|medium|low"}\n'
        "or {\"found\":false}\n\n"
        "Rules:\n"
        "- title_raw: exact on-screen movie title if visible; else international title.\n"
        f"- title: same movie in {lang_name} (local name). Same year. "
        "Never a different film.\n"
        f"- summary: 2-3 short sentences in {lang_name} about THIS film only.\n"
        "- Prefer on-screen title over Instagram captions / guessing.\n"
        "- If unknown: {\"found\":false}"
    )

    try:
        async with httpx.AsyncClient(timeout=45, headers=_http_headers()) as client:
            data = image_bytes
            ctype = mime or "image/jpeg"
            if data is None and image_url:
                data, ctype = await _download_image(client, image_url)
            if not data:
                return None
            b64 = base64.b64encode(data[:2_000_000]).decode("ascii")
            image_part = {"inline_data": {"mime_type": ctype, "data": b64}}

            # 1) OCR / oddiy nom — eng ishonchli
            for prompt in plain_prompts:
                text_out, model = await _gemini_generate_text(
                    client, api_key, [{"text": prompt}, image_part]
                )
                if not text_out:
                    continue
                if text_out.upper().startswith("UNKNOWN"):
                    continue
                from_ocr = extract_movie_from_ocr_text(text_out)
                if from_ocr:
                    return {
                        "ok": True,
                        "title": from_ocr,
                        "title_raw": from_ocr,
                        "summary": "",
                        "localized": False,
                        "source": f"Internet · Gemini OCR ({model})",
                        "error": "",
                    }
                line = text_out.splitlines()[0].strip().strip("`\"'")
                movie = (
                    normalize_movie_hit(line, line)
                    or extract_movie_from_ocr_text(line)
                    or clean_title(line)
                )
                if movie and not looks_like_prose(movie):
                    return {
                        "ok": True,
                        "title": movie,
                        "title_raw": movie,
                        "summary": "",
                        "localized": False,
                        "source": f"Internet · Gemini ({model})",
                        "error": "",
                    }

            # 2) JSON: lokal nom + mazmun
            text_out, model = await _gemini_generate_text(
                client, api_key, [{"text": json_prompt}, image_part]
            )
            parsed = _parse_gemini_movie_json(text_out)
            if parsed and parsed.get("found") and parsed.get("title"):
                raw = parsed.get("title_raw") or parsed["title"]
                local = parsed["title"]
                # Lokal nom boshqa film bo‘lsa — raw ni saqlaymiz
                if parsed.get("title_raw") and not titles_same_movie(raw, local):
                    local = raw
                return {
                    "ok": True,
                    "title": local,
                    "title_raw": raw,
                    "summary": parsed.get("summary") or "",
                    "localized": bool(parsed.get("summary")),
                    "source": f"Internet · Gemini ({model})",
                    "error": "",
                }
    except Exception as e:
        print(f"gemini_identify_movie error: {type(e).__name__}: {e}", flush=True)
        return None
    return None


async def identify_movie_from_image_bytes(
    image_bytes: bytes,
    mime: str = "image/jpeg",
    lang: str = "uz",
    on_progress: ProgressCb | None = None,
) -> dict:
    """Telegram orqali yuborilgan screenshot/rasmni aniqlash."""
    if not image_bytes:
        return {"ok": False, "title": "", "summary": "", "source": "", "error": "no_image"}

    has_key = bool(_gemini_api_key())
    print(
        f"identify_image: bytes={len(image_bytes)} mime={mime} lang={lang} gemini={has_key}",
        flush=True,
    )

    if has_key:
        await _progress(on_progress, "ai")
        ghit = await gemini_identify_movie(
            image_bytes=image_bytes, mime=mime, lang=lang
        )
        if ghit and ghit.get("ok"):
            return await ensure_localized_result(ghit, lang, on_progress=on_progress)

    # Yandex — Gemini bo‘lmasa yoki yiqilsa
    try:
        await _progress(on_progress, "search")
        async with httpx.AsyncClient(
            timeout=FETCH_TIMEOUT, follow_redirects=True, headers=_http_headers()
        ) as client:
            hit = await yandex_reverse_image_movie(
                client, image_bytes=image_bytes, mime=mime
            )
            if hit and hit.get("ok"):
                return await ensure_localized_result(hit, lang, on_progress=on_progress)
    except Exception as e:
        print(f"yandex image identify error: {e}", flush=True)

    if not has_key:
        return {
            "ok": False,
            "title": "",
            "summary": "",
            "source": "",
            "error": "need_gemini",
        }
    return {
        "ok": False,
        "title": "",
        "summary": "",
        "source": "",
        "error": "not_identified",
    }


def extract_jpeg_frame_from_video(video_bytes: bytes, at_seconds: float = 1.0) -> bytes | None:
    """
    Videodan bitta JPEG kadr (faqat aniqlash uchun).
    Video saqlanmaydi/tarqatilmaydi.
    """
    import subprocess
    import tempfile
    from pathlib import Path

    if not video_bytes or len(video_bytes) < 1000:
        return None
    # Telegram Bot API getFile limiti ~20MB
    if len(video_bytes) > 20 * 1024 * 1024:
        return None

    with tempfile.TemporaryDirectory(prefix="soyla_vid_") as tmp:
        inp = Path(tmp) / "in.bin"
        out = Path(tmp) / "frame.jpg"
        inp.write_bytes(video_bytes)
        # Avval at_seconds, bo‘lmasa 0-soniya
        for ss in (max(0.0, at_seconds), 0.0, 2.0, 0.5):
            try:
                proc = subprocess.run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-ss",
                        str(ss),
                        "-i",
                        str(inp),
                        "-frames:v",
                        "1",
                        "-q:v",
                        "2",
                        "-update",
                        "1",
                        str(out),
                    ],
                    capture_output=True,
                    timeout=25,
                    check=False,
                )
                if proc.returncode == 0 and out.exists() and out.stat().st_size > 200:
                    return out.read_bytes()
            except Exception:
                continue
    return None


async def identify_movie_from_video_bytes(
    video_bytes: bytes,
    lang: str = "uz",
    on_progress: ProgressCb | None = None,
) -> dict:
    """Yuborilgan video fayldan kadr olib film nomini aniqlash."""
    if not video_bytes:
        return {"ok": False, "title": "", "summary": "", "source": "", "error": "no_image"}
    if len(video_bytes) > 20 * 1024 * 1024:
        return {
            "ok": False,
            "title": "",
            "summary": "",
            "source": "",
            "error": "video_too_large",
        }

    await _progress(on_progress, "frame")
    frame = extract_jpeg_frame_from_video(video_bytes, at_seconds=1.0)
    if not frame:
        return {"ok": False, "title": "", "summary": "", "source": "", "error": "no_frame"}

    result = await identify_movie_from_image_bytes(
        frame, "image/jpeg", lang=lang, on_progress=on_progress
    )
    if result.get("ok") and result.get("source"):
        result["source"] = f"{result['source']} · video kadr"
    return result


def _ytdlp_cookies_file() -> str:
    import os
    from pathlib import Path

    path = (os.environ.get("YTDLP_COOKIES_FILE") or "").strip()
    if not path:
        try:
            from app.config import settings

            path = (getattr(settings, "ytdlp_cookies_file", "") or "").strip()
        except Exception:
            path = ""
    if path and Path(path).is_file():
        return path
    return ""


def yt_dlp_fetch_for_identify(url: str) -> dict:
    """
    Silka orqali (faqat aniqlash uchun) thumbnail yoki qisqa video olish.
    Video foydalanuvchiga yuborilmaydi / saqlanmaydi.
    Qaytaradi: {thumbnail_url, video_bytes, error}
    """
    import tempfile
    from pathlib import Path

    out: dict = {"thumbnail_url": "", "video_bytes": b"", "error": ""}
    try:
        import yt_dlp
    except Exception:
        out["error"] = "yt_dlp_missing"
        return out

    cookies = _ytdlp_cookies_file()
    with tempfile.TemporaryDirectory(prefix="soyla_ytdlp_") as tmp:
        tmp_path = Path(tmp)
        outtmpl = str(tmp_path / "media.%(ext)s")
        opts = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "noprogress": True,
            "format": "best[height<=720]/best",
            "max_filesize": 18 * 1024 * 1024,
            "socket_timeout": 20,
            "retries": 1,
        }
        if cookies:
            opts["cookiefile"] = cookies

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
            if not info:
                out["error"] = "no_info"
                return out
            thumb = (info.get("thumbnail") or "").strip()
            if not thumb:
                thumbs = info.get("thumbnails") or []
                if thumbs:
                    thumb = (thumbs[-1].get("url") or "").strip()
            out["thumbnail_url"] = thumb

            # Yuklangan fayl
            req = info.get("requested_downloads") or []
            filepath = ""
            if req and req[0].get("filepath"):
                filepath = req[0]["filepath"]
            if not filepath:
                # fallback: tmp dagi birinchi media
                files = list(tmp_path.glob("media.*"))
                if files:
                    filepath = str(files[0])
            if filepath and Path(filepath).is_file():
                data = Path(filepath).read_bytes()
                if 1000 < len(data) <= 20 * 1024 * 1024:
                    out["video_bytes"] = data
            if not out["video_bytes"] and not out["thumbnail_url"]:
                out["error"] = "empty"
            return out
        except Exception as e:
            out["error"] = type(e).__name__
            return out


async def _identify_from_social_download(
    url: str,
    host: str,
    lang: str = "uz",
    on_progress: ProgressCb | None = None,
) -> dict | None:
    """Silka orqali video/thumb yuklab aniqlash (best-effort)."""
    import asyncio

    await _progress(on_progress, "auto_dl")
    fetched = await asyncio.to_thread(yt_dlp_fetch_for_identify, url)
    video_bytes = fetched.get("video_bytes") or b""
    thumb = fetched.get("thumbnail_url") or ""

    if video_bytes:
        result = await identify_movie_from_video_bytes(
            video_bytes, lang=lang, on_progress=on_progress
        )
        if result.get("ok"):
            result["host"] = host
            src = result.get("source") or "Internet"
            result["source"] = f"{src} · auto-download"
            return result

    if thumb:
        try:
            async with httpx.AsyncClient(
                timeout=FETCH_TIMEOUT, follow_redirects=True, headers=_http_headers()
            ) as client:
                img_bytes, mime = await _download_image(client, thumb)
            if img_bytes:
                if _gemini_api_key():
                    await _progress(on_progress, "ai")
                    ghit = await gemini_identify_movie(
                        image_url=thumb,
                        image_bytes=img_bytes,
                        mime=mime,
                        lang=lang,
                    )
                    if ghit and ghit.get("ok"):
                        ghit["host"] = host
                        ghit["source"] = f"{ghit.get('source')} · auto-thumb"
                        return await ensure_localized_result(
                            ghit, lang, on_progress=on_progress
                        )
                await _progress(on_progress, "search")
                async with httpx.AsyncClient(
                    timeout=FETCH_TIMEOUT, follow_redirects=True, headers=_http_headers()
                ) as client:
                    hit = await yandex_reverse_image_movie(
                        client, image_url=thumb, image_bytes=img_bytes, mime=mime
                    )
                if hit and hit.get("ok"):
                    hit["host"] = host
                    hit["source"] = f"{hit.get('source')} · auto-thumb"
                    return await ensure_localized_result(
                        hit, lang, on_progress=on_progress
                    )
        except Exception:
            pass
    return None


async def fetch_page_title(
    url: str, lang: str = "uz", on_progress: ProgressCb | None = None
) -> dict:
    """
    Asosiy API: {ok, title, summary, source, host, error}
    Caption emas — preview kadr + internet/AI.
    Social silkalarda kerak bo‘lsa yt-dlp orqali avtomatik yuklab (faqat aniqlash).
    Nom va mazmun app tilida (lang).
    """
    url = normalize_media_url(url)
    host = _host_hint(url)
    social = _host_matches(host, SOCIAL_HOSTS)

    try:
        await _progress(on_progress, "preview")
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
                    await _progress(on_progress, "ai")
                    ghit = await gemini_identify_movie(
                        image_url=thumb,
                        image_bytes=img_bytes,
                        mime=mime,
                        lang=lang,
                    )
                    if ghit and ghit.get("ok"):
                        ghit["host"] = host
                        return await ensure_localized_result(
                            ghit, lang, on_progress=on_progress
                        )

                await _progress(on_progress, "search")
                hit = await yandex_reverse_image_movie(
                    client, image_url=thumb, image_bytes=img_bytes, mime=mime
                )
                if hit and hit.get("ok"):
                    hit["host"] = host
                    return await ensure_localized_result(
                        hit, lang, on_progress=on_progress
                    )

            elif thumb:
                await _progress(on_progress, "search")
                hit = await yandex_reverse_image_movie(
                    client, image_url=thumb, image_bytes=img_bytes, mime=mime
                )
                if hit and hit.get("ok"):
                    hit["host"] = host
                    return await ensure_localized_result(
                        hit, lang, on_progress=on_progress
                    )
                await _progress(on_progress, "ai")
                ghit = await gemini_identify_movie(
                    image_url=thumb,
                    image_bytes=img_bytes,
                    mime=mime,
                    lang=lang,
                )
                if ghit and ghit.get("ok"):
                    ghit["host"] = host
                    return await ensure_localized_result(
                        ghit, lang, on_progress=on_progress
                    )

            if not social and page_title and not looks_like_prose(page_title):
                if YEAR_IN_TEXT_RE.search(page_title) or len(page_title) <= 80:
                    return await ensure_localized_result(
                        {
                            "ok": True,
                            "title": page_title,
                            "summary": "",
                            "source": site or host or "link",
                            "host": host,
                            "error": "",
                        },
                        lang,
                        on_progress=on_progress,
                    )

        # Social (yoki preview yo‘q): silka orqali avtomatik yuklab aniqlash
        if social or not thumb:
            auto = await _identify_from_social_download(
                url, host, lang=lang, on_progress=on_progress
            )
            if auto and auto.get("ok"):
                return auto

        if social and not _gemini_api_key():
            return {
                "ok": False,
                "title": "",
                "summary": "",
                "source": "",
                "host": host,
                "error": "need_gemini",
            }

        return {
            "ok": False,
            "title": "",
            "summary": "",
            "source": "",
            "host": host,
            "error": "no_image" if not thumb else "not_identified",
        }
    except Exception as e:
        return {
            "ok": False,
            "title": "",
            "summary": "",
            "source": "",
            "host": host,
            "error": type(e).__name__,
        }


async def resolve_movie_title_from_message(
    message, lang: str = "uz", on_progress: ProgressCb | None = None
) -> dict:
    urls = extract_urls_from_message(message)
    if not urls:
        return {"ok": False, "error": "no_url", "title": "", "summary": "", "url": ""}
    url = urls[0]
    result = await fetch_page_title(url, lang=lang, on_progress=on_progress)
    result["url"] = url
    return result
