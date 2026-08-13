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
    {"id": "speak_uz", "uz": "O'zbek speaking", "ru": "Узбекский speaking", "en": "Uzbek speaking"},
]

TOPIC_IDS = {t["id"] for t in MATCH_TOPICS}
DEFAULT_TOPIC = "any"


def topic_compatible(a: str | None, b: str | None) -> bool:
    """Ikkalasi bir xil mavzu yoki bir tomon 'any'."""
    ta = (a or DEFAULT_TOPIC).strip() or DEFAULT_TOPIC
    tb = (b or DEFAULT_TOPIC).strip() or DEFAULT_TOPIC
    if ta not in TOPIC_IDS:
        ta = DEFAULT_TOPIC
    if tb not in TOPIC_IDS:
        tb = DEFAULT_TOPIC
    if ta == "any" or tb == "any":
        return True
    return ta == tb


def topic_label(topic_id: str, lang: str = "uz") -> str:
    for t in MATCH_TOPICS:
        if t["id"] == topic_id:
            return t.get(lang) or t["uz"]
    return topic_id
