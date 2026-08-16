"""Vaqtinchalik ban eskalatsiyasi — blok (soat) va shikoyat (kun)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select

from app.database import async_session
from app.models import User
from app.telegram_client import send_message


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_temp_banned(user: User | None) -> bool:
    if not user:
        return False
    if user.is_banned:
        return True
    until = _aware(getattr(user, "ban_until", None))
    return bool(until and until > _utcnow())


def ban_remaining_seconds(user: User | None) -> int:
    if not user or user.is_banned:
        return 0
    until = _aware(getattr(user, "ban_until", None))
    if not until:
        return 0
    return max(0, int((until - _utcnow()).total_seconds()))


def call_ban_detail(user: User | None) -> str | None:
    """Agar chaqiruv/qidiruv taqiqlangan bo‘lsa — foydalanuvchiga xabar matni."""
    if not user:
        return None
    if user.is_banned:
        return "Hisobingiz cheklangan"
    if not is_temp_banned(user):
        return None
    secs = ban_remaining_seconds(user)
    if secs >= 86400:
        days = max(1, (secs + 86399) // 86400)
        return f"Chaqiruvlar cheklangan. Qolgan muddat: ~{days} kun"
    hours = max(1, (secs + 3599) // 3600)
    return f"Chaqiruvlar cheklangan. Qolgan muddat: ~{hours} soat"


def apply_block_strike_on_user(user: User) -> dict:
    """Blok: 2 soat, keyin 4, 8… (session ichida)."""
    strikes = int(getattr(user, "block_strike_count", 0) or 0) + 1
    user.block_strike_count = strikes
    hours = min(2 * (2 ** (strikes - 1)), 24 * 30)
    until = _utcnow() + timedelta(hours=hours)
    cur = _aware(getattr(user, "ban_until", None))
    if cur is None or until > cur:
        user.ban_until = until
    return {
        "kind": "block",
        "hours": hours,
        "strikes": strikes,
        "ban_until": user.ban_until,
    }


def apply_report_strike_on_user(user: User) -> dict:
    """Shikoyat: 1 kun, keyin 2, 4… (session ichida)."""
    strikes = int(getattr(user, "report_strike_count", 0) or 0) + 1
    user.report_strike_count = strikes
    days = min(1 * (2 ** (strikes - 1)), 365)
    until = _utcnow() + timedelta(days=days)
    cur = _aware(getattr(user, "ban_until", None))
    if cur is None or until > cur:
        user.ban_until = until
    return {
        "kind": "report",
        "days": days,
        "strikes": strikes,
        "ban_until": user.ban_until,
    }


async def notify_strike(user_id: int, info: dict) -> None:
    try:
        if info.get("kind") == "block":
            text = (
                f"⛔ Sizni bloklashdi. Chaqiruvlar {info['hours']} soatga cheklangan "
                f"(#{info['strikes']}-marta).\nMuddat tugaguncha video qidiruv ishlamaydi."
            )
        else:
            text = (
                f"⛔ Sizga shikoyat keldi. Chaqiruvlar {info['days']} kunga cheklangan "
                f"(#{info['strikes']}-marta).\nMuddat tugaguncha video qidiruv ishlamaydi."
            )
        await send_message(user_id, text)
    except Exception:
        pass


async def get_banned_or_restricted_ids() -> set[int]:
    """Doimiy ban + muddati o‘tmagan vaqtinchalik ban."""
    now = _utcnow()
    async with async_session() as session:
        rows = await session.execute(
            select(User.id).where(
                or_(
                    User.is_banned.is_(True),
                    (User.ban_until.is_not(None)) & (User.ban_until > now),
                )
            )
        )
        return set(rows.scalars().all())
