"""Mavzuli match — sozlamada tanlanadi, matchingda mos kelishi kerak."""

from __future__ import annotations

# id → labels
MATCH_TOPICS: list[dict] = [
    {"id": "any", "uz": "Farqi yo'q", "ru": "Неважно", "en": "Anything"},
    {"id": "friends", "uz": "Do'st topish", "ru": "Найти друзей", "en": "Find friends"},
    {"id": "dating", "uz": "Juft / tanishuv", "ru": "Пара / знакомства", "en": "Dating"},
    {"id": "study", "uz": "Ilmiy / o'qish", "ru": "Учёба / наука", "en": "Study"},
    {"id": "speak_en", "uz": "Ingliz speaking", "ru": "English speaking", "en": "English speaking"},
    {"id": "speak_de", "uz": "Nemis speaking", "ru": "Deutsch speaking", "en": "German speaking"},
    {"id": "speak_ru", "uz": "Rus speaking", "ru": "Русский speaking", "en": "Russian speaking"},
    {"id": "speak_tg", "uz": "Tojik speaking", "ru": "Таджикский speaking", "en": "Tajik speaking"},
    {"id": "speak_tr", "uz": "Turk speaking", "ru": "Турецкий speaking", "en": "Turkish speaking"},
    {"id": "speak_ko", "uz": "Koreys speaking", "ru": "Корейский speaking", "en": "Korean speaking"},
    {"id": "speak_ja", "uz": "Yapon speaking", "ru": "Японский speaking", "en": "Japanese speaking"},
    {"id": "speak_zh", "uz": "Xitoy speaking", "ru": "Китайский speaking", "en": "Chinese speaking"},
]

TOPIC_IDS = {t["id"] for t in MATCH_TOPICS}
DEFAULT_TOPIC = "any"

# Eski id lar → yangi
LEGACY_TOPIC_MAP = {
    "speak_uz": "any",
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
