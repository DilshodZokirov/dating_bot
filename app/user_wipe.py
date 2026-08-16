"""Foydalanuvchi profilini to‘liq o‘chirish (qayta ro‘yxat uchun)."""

from __future__ import annotations

from sqlalchemy import delete, or_, select

from app.avatars import delete_avatar_files
from app.database import async_session
from app.matching.queue import cancel_proposals_by_user, cancel_wait
from app.models import (
    Block,
    CallFeedback,
    CallSession,
    ChatInvite,
    ChatMessage,
    ChatThread,
    PhoneShareRequest,
    Report,
    SavedPartner,
    User,
)


async def wipe_user(user_id: int) -> bool:
    """
    Foydalanuvchi va bog‘liq yozuvlarni o‘chiradi.
    True — o‘chirildi, False — user topilmadi.
    """
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return False

        looking = user.looking_for.value if user.looking_for else "any"

        # Chat xabarlari (thread orqali + sender)
        thread_ids = list(
            (
                await session.execute(
                    select(ChatThread.id).where(
                        or_(ChatThread.user_a_id == user_id, ChatThread.user_b_id == user_id)
                    )
                )
            ).scalars().all()
        )
        if thread_ids:
            await session.execute(
                delete(ChatMessage).where(ChatMessage.thread_id.in_(thread_ids))
            )
        await session.execute(
            delete(ChatMessage).where(ChatMessage.sender_id == user_id)
        )
        await session.execute(
            delete(ChatThread).where(
                or_(ChatThread.user_a_id == user_id, ChatThread.user_b_id == user_id)
            )
        )
        await session.execute(
            delete(ChatInvite).where(
                or_(ChatInvite.from_user_id == user_id, ChatInvite.to_user_id == user_id)
            )
        )
        await session.execute(
            delete(SavedPartner).where(
                or_(SavedPartner.user_id == user_id, SavedPartner.partner_id == user_id)
            )
        )
        await session.execute(
            delete(Block).where(
                or_(Block.blocker_id == user_id, Block.blocked_id == user_id)
            )
        )
        await session.execute(
            delete(Report).where(
                or_(Report.reporter_id == user_id, Report.reported_id == user_id)
            )
        )
        await session.execute(
            delete(CallFeedback).where(
                or_(CallFeedback.from_user_id == user_id, CallFeedback.to_user_id == user_id)
            )
        )
        await session.execute(
            delete(CallSession).where(
                or_(CallSession.user1_id == user_id, CallSession.user2_id == user_id)
            )
        )
        await session.execute(
            delete(PhoneShareRequest).where(
                or_(
                    PhoneShareRequest.from_user_id == user_id,
                    PhoneShareRequest.to_user_id == user_id,
                )
            )
        )

        await session.delete(user)
        await session.commit()

    try:
        await cancel_wait(user_id, looking)
    except Exception:
        pass
    try:
        await cancel_proposals_by_user(user_id)
    except Exception:
        pass
    try:
        delete_avatar_files(user_id)
    except Exception:
        pass

    return True
