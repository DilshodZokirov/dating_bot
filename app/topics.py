"""Mavzuli match — sozlamada tanlanadi, matchingda mos kelishi kerak.

Til (language) alohida: matching allaqachon bir xil til bo'yicha filtrlaydi.
Speaking mavzular olib tashlandi — tillar profil Til maydonida.
"""

from __future__ import annotations

# id → labels (faqat suhbat maqsadi; til emas)
MATCH_TOPICS: list[dict] = [
    {"id": "any", "uz": "Farqi yo'q", "ru": "Неважно", "en": "Anything"},
    {"id": "friends", "uz": "Do'st topish", "ru": "Найти друзей", "en": "Find friends"},
    {"id": "dating", "uz": "Juft / tanishuv", "ru": "Пара / знакомства", "en": "Dating"},
    {"id": "study", "uz": "Ilmiy / o'qish", "ru": "Учёба / наука", "en": "Study"},
]

TOPIC_IDS = {t["id"] for t in MATCH_TOPICS}
DEFAULT_TOPIC = "any"

# Eski speaking mavzular → any (til endi Language da)
LEGACY_TOPIC_MAP = {
    "speak_uz": "any",
    "speak_en": "any",
    "speak_de": "any",
    "speak_ru": "any",
    "speak_tg": "any",
    "speak_tr": "any",
    "speak_ko": "any",
    "speak_ja": "any",
    "speak_zh": "any",
}


def normalize_topic(topic: str | None) -> str:
    t = (topic or DEFAULT_TOPIC).strip() or DEFAULT_TOPIC
    t = LEGACY_TOPIC_MAP.get(t, t)
    if t not in TOPIC_IDS:
        return DEFAULT_TOPIC
    return t


def topic_compatible(a: str | None, b: str | None) -> bool:
    """Ikkalasi bir xil mavzu yoki bir tomon 'any'."""
    ta = normalize_topic(a)
    tb = normalize_topic(b)
    if ta == "any" or tb == "any":
        return True
    return ta == tb


def topic_label(topic_id: str, lang: str = "uz") -> str:
    tid = normalize_topic(topic_id)
    for t in MATCH_TOPICS:
        if t["id"] == tid:
            return t.get(lang) or t["uz"]
    return tid
