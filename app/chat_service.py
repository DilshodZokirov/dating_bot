"""Sevimlilar (o‘zaro saqlash) + chat thread yordamchilari."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatThread, SavedPartner


def ordered_pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


async def ensure_saved(session: AsyncSession, user_id: int, partner_id: int) -> None:
    if user_id == partner_id:
        return
    existing = (
        await session.execute(
            select(SavedPartner).where(
                SavedPartner.user_id == user_id, SavedPartner.partner_id == partner_id
            )
        )
    ).scalar_one_or_none()
    if not existing:
        session.add(SavedPartner(user_id=user_id, partner_id=partner_id))


async def ensure_mutual_favorites_and_thread(
    session: AsyncSession, user_id: int, partner_id: int
) -> ChatThread:
    """Ikkalasini ham sevimlilarga qo‘shadi va chat thread ochadi/qaytaradi."""
    await ensure_saved(session, user_id, partner_id)
    await ensure_saved(session, partner_id, user_id)

    a, b = ordered_pair(user_id, partner_id)
    thread = (
        await session.execute(
            select(ChatThread).where(ChatThread.user_a_id == a, ChatThread.user_b_id == b)
        )
    ).scalar_one_or_none()
    if not thread:
        thread = ChatThread(user_a_id=a, user_b_id=b)
        session.add(thread)
        await session.flush()
    return thread


async def get_thread_for_pair(session: AsyncSession, user_id: int, partner_id: int) -> ChatThread | None:
    a, b = ordered_pair(user_id, partner_id)
    return (
        await session.execute(
            select(ChatThread).where(ChatThread.user_a_id == a, ChatThread.user_b_id == b)
        )
    ).scalar_one_or_none()


async def thread_partner_id(thread: ChatThread, me_id: int) -> int | None:
    if thread.user_a_id == me_id:
        return thread.user_b_id
    if thread.user_b_id == me_id:
        return thread.user_a_id
    return None


async def user_threads(session: AsyncSession, me_id: int) -> list[ChatThread]:
    rows = await session.execute(
        select(ChatThread)
        .where(or_(ChatThread.user_a_id == me_id, ChatThread.user_b_id == me_id))
        .order_by(ChatThread.updated_at.desc(), ChatThread.id.desc())
    )
    return list(rows.scalars().all())
