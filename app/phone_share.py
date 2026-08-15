"""Telefon raqam so‘rovi / ulashish."""

from __future__ import annotations

from datetime import datetime, timezone

from app.database import async_session
from app.i18n import t
from app.matching.queue import redis_client
from app.models import PhoneShareRequest, PhoneShareStatus, User
from app.telegram_client import contact_request_keyboard, notify_admins, send_message


def _ui_lang(user: User | None) -> str:
    if not user:
        return "uz"
    ui = getattr(user, "ui_language", None)
    if ui is not None:
        return ui.value if hasattr(ui, "value") else str(ui)
    return user.language.value if hasattr(user.language, "value") else str(user.language)


async def deliver_phone_to_requester(request_id: int, sharer_id: int) -> bool:
    async with async_session() as session:
        req = await session.get(PhoneShareRequest, request_id)
        sharer = await session.get(User, sharer_id)
        if not req or not sharer:
            return False
        phone = (sharer.phone or "").strip()
        if not phone:
            return False
        requester = await session.get(User, req.from_user_id)
        from_id = req.from_user_id
        room_id = req.room_id
        name = sharer.name

    lang = _ui_lang(requester)
    try:
        await send_message(from_id, t(lang, "phone_shared", name=name, phone=phone))
    except Exception as e:
        print(f"phone deliver {from_id}: {e}", flush=True)
    await notify_admins(
        f"📱 Telefon ulashildi\n"
        f"Kim: <code>{sharer_id}</code> ({name})\n"
        f"Kimga: <code>{from_id}</code>\n"
        f"Tel: <code>{phone}</code>\n"
        f"Xona: {room_id}"
    )
    return True


async def save_user_phone(user_id: int, phone: str) -> User | None:
    phone = (phone or "").strip()[:32]
    if not phone:
        return None
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return None
        user.phone = phone
        await session.commit()
        await session.refresh(user)
        return user


async def accept_phone_share(request_id: int, user_id: int) -> dict:
    async with async_session() as session:
        req = await session.get(PhoneShareRequest, request_id)
        if not req or req.to_user_id != user_id:
            return {"status": "invalid"}
        if req.status != PhoneShareStatus.pending:
            return {"status": "closed"}
        me = await session.get(User, user_id)
        req.status = PhoneShareStatus.accepted
        req.responded_at = datetime.now(timezone.utc)
        await session.commit()
        phone = (me.phone or "").strip() if me else ""

    if phone:
        await deliver_phone_to_requester(request_id, user_id)
        return {"status": "shared"}

    await redis_client.set(f"phone:await:{user_id}", str(request_id), ex=900)
    lang = _ui_lang(me)
    try:
        await send_message(
            user_id,
            t(lang, "phone_need_contact"),
            reply_markup=contact_request_keyboard(t(lang, "btn_share_contact")),
        )
    except Exception as e:
        print(f"phone contact ask {user_id}: {e}", flush=True)
    return {"status": "need_contact"}


async def decline_phone_share(request_id: int, user_id: int) -> dict:
    async with async_session() as session:
        req = await session.get(PhoneShareRequest, request_id)
        if not req or req.to_user_id != user_id:
            return {"status": "invalid"}
        if req.status != PhoneShareStatus.pending:
            return {"status": "closed"}
        req.status = PhoneShareStatus.declined
        req.responded_at = datetime.now(timezone.utc)
        from_id = req.from_user_id
        await session.commit()
    try:
        await send_message(from_id, "❌ Suhbatdosh telefon raqamini ulashishni rad etdi.")
    except Exception:
        pass
    return {"status": "declined"}


async def complete_phone_await_after_contact(user_id: int, phone: str) -> bool:
    """Contact kelganda kutayotgan so‘rovni yakunlash."""
    await save_user_phone(user_id, phone)
    raw = await redis_client.get(f"phone:await:{user_id}")
    if not raw:
        return False
    await redis_client.delete(f"phone:await:{user_id}")
    request_id = int(raw)
    async with async_session() as session:
        req = await session.get(PhoneShareRequest, request_id)
        if not req or req.to_user_id != user_id:
            return False
        if req.status == PhoneShareStatus.pending:
            req.status = PhoneShareStatus.accepted
            req.responded_at = datetime.now(timezone.utc)
            await session.commit()
    return await deliver_phone_to_requester(request_id, user_id)
