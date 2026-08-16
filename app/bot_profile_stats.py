"""Bot profilidagi ochiq statistika — hamma ko‘radi (short description)."""

from __future__ import annotations

import asyncio
import logging
from time import monotonic

from aiogram import Bot
from sqlalchemy import func, select

from app.database import async_session
from app.models import User

logger = logging.getLogger(__name__)

# Short description limitleari (Telegram)
_SHORT_MAX = 120
_DESC_MAX = 512

_last_count: int | None = None
_last_push_at = 0.0
_MIN_PUSH_INTERVAL_SEC = 60.0


async def get_users_count() -> int:
    async with async_session() as session:
        n = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
    return int(n)


def format_users_line(lang: str, count: int) -> str:
    n = f"{count:,}".replace(",", " ")
    lines = {
        "uz": f"👥 Soyla’da hozir <b>{n}</b> ta foydalanuvchi",
        "ru": f"👥 Сейчас в Soyla: <b>{n}</b> пользователей",
        "en": f"👥 Soyla now has <b>{n}</b> users",
        "de": f"👥 Soyla hat jetzt <b>{n}</b> Nutzer",
        "tg": f"👥 Ҳоло дар Soyla: <b>{n}</b> корбар",
        "tr": f"👥 Soyla’da şu an <b>{n}</b> kullanıcı",
        "ko": f"👥 Soyla 현재 사용자 <b>{n}</b>명",
        "ja": f"👥 Soylaの利用者は現在 <b>{n}</b>人",
        "zh": f"👥 Soyla 当前有 <b>{n}</b> 位用户",
        "ar": f"👥 يوجد الآن في Soyla <b>{n}</b> مستخدمًا",
    }
    return lines.get(lang) or lines["uz"]


def _short_for_lang(lang: str | None, count: int) -> str:
    n = f"{count:,}".replace(",", " ")
    texts = {
        None: f"Soyla · speaking, do‘st, juft · {n} foydalanuvchi",
        "uz": f"Soyla · speaking, do‘st, juft · {n} foydalanuvchi",
        "ru": f"Soyla · speaking, друзья, пара · {n} пользователей",
        "en": f"Soyla · speaking, friends, dating · {n} users",
    }
    text = texts.get(lang, texts[None])
    return text[:_SHORT_MAX]


def _desc_for_lang(lang: str | None, count: int) -> str:
    n = f"{count:,}".replace(",", " ")
    texts = {
        None: (
            f"Soyla — speaking partner, do‘st va juft topish.\n"
            f"Video qo‘ng‘iroq · chat · 10 til.\n"
            f"Hozir: {n} ta foydalanuvchi.\n"
            f"Boshlash: /start yoki Menu → Qidirish"
        ),
        "uz": (
            f"Soyla — speaking partner, do‘st va juft topish.\n"
            f"Video qo‘ng‘iroq · chat · 10 til.\n"
            f"Hozir: {n} ta foydalanuvchi.\n"
            f"Boshlash: /start yoki Menu → Qidirish"
        ),
        "ru": (
            f"Soyla — speaking, друзья и знакомства.\n"
            f"Видеозвонок · чат · 10 языков.\n"
            f"Сейчас: {n} пользователей.\n"
            f"Старт: /start или Menu → Поиск"
        ),
        "en": (
            f"Soyla — speaking partners, friends and dating.\n"
            f"Video calls · chat · 10 languages.\n"
            f"Now: {n} users.\n"
            f"Start: /start or Menu → Search"
        ),
    }
    text = texts.get(lang, texts[None])
    return text[:_DESC_MAX]


async def refresh_bot_public_profile(bot: Bot, *, force: bool = False) -> int:
    """Botning yuqorisidagi short/description ni yangilaydi (hamma ko‘radi)."""
    global _last_count, _last_push_at

    count = await get_users_count()
    now = monotonic()
    if (
        not force
        and _last_count == count
        and (now - _last_push_at) < _MIN_PUSH_INTERVAL_SEC
    ):
        return count

    for lang in (None, "uz", "ru", "en"):
        try:
            await bot.set_my_short_description(
                short_description=_short_for_lang(lang, count),
                language_code=lang,
            )
        except Exception as e:
            logger.warning("set_my_short_description(%s) failed: %s", lang, e)
        try:
            await bot.set_my_description(
                description=_desc_for_lang(lang, count),
                language_code=lang,
            )
        except Exception as e:
            logger.warning("set_my_description(%s) failed: %s", lang, e)

    _last_count = count
    _last_push_at = now
    logger.info("Bot public profile updated: users=%s", count)
    return count


async def public_profile_loop(bot: Bot, interval_sec: int = 300) -> None:
    """Har N daqiqada profilni yangilab turadi."""
    while True:
        try:
            await refresh_bot_public_profile(bot, force=True)
        except Exception as e:
            logger.warning("public_profile_loop: %s", e)
        await asyncio.sleep(max(60, interval_sec))
