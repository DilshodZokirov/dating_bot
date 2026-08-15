"""Taklifga javob — API va bot uchun umumiy."""

from __future__ import annotations

import uuid

from app.chat_service import ensure_mutual_favorites_and_thread
from app.database import async_session
from app.i18n import t
from app.livekit_tokens import livekit_configured, livekit_join_payload
from app.matching.queue import requeue_user, set_decision, set_result
from app.models import CallSession, User
from app.telegram_client import notify_admins, send_message, webapp_open_keyboard


def _other_side(proposal: dict, responder_id: int) -> dict:
    if responder_id == proposal["requester_id"]:
        prefix = "candidate"
    else:
        prefix = "requester"
    return {
        "user_id": proposal[f"{prefix}_id"],
        "gender": proposal[f"{prefix}_gender"],
        "looking_for": proposal[f"{prefix}_looking_for"],
        "age": proposal[f"{prefix}_age"],
        "language": proposal[f"{prefix}_language"],
        "city": proposal[f"{prefix}_city"],
        "search_scope": proposal[f"{prefix}_search_scope"],
        "prefer_age_min": proposal.get(f"{prefix}_prefer_age_min", 12),
        "prefer_age_max": proposal.get(f"{prefix}_prefer_age_max", 100),
        "match_topic": proposal.get(f"{prefix}_match_topic", "any"),
    }


def _ui_lang(user: User | None) -> str:
    if not user:
        return "uz"
    ui = getattr(user, "ui_language", None)
    if ui is not None:
        return ui.value if hasattr(ui, "value") else str(ui)
    return user.language.value if hasattr(user.language, "value") else str(user.language)


async def _notify_match_open(user: User | None, partner_name: str) -> None:
    if not user:
        return
    lang = _ui_lang(user)
    kb = webapp_open_keyboard(t(lang, "menu_btn"))
    try:
        await send_message(
            user.id,
            t(lang, "match_started") + f"\n\n👤 {partner_name}",
            reply_markup=kb,
        )
    except Exception as e:
        print(f"match notify {user.id}: {e}", flush=True)


async def respond_to_proposal(user_id: int, proposal_id: str, decision: str) -> dict:
    if decision not in ("accepted", "declined"):
        return {"outcome": "invalid"}

    result = await set_decision(proposal_id, user_id, decision)

    if result["status"] == "invalid":
        return {"outcome": "invalid"}

    if result["status"] == "waiting_partner":
        return {"outcome": "waiting_partner"}

    proposal = result["proposal"]
    other = _other_side(proposal, user_id)

    if result["status"] == "declined":
        await requeue_user(other)
        await set_result(other["user_id"], "requeued")
        try:
            await send_message(
                other["user_id"],
                "❌ Suhbatdosh chaqiruvni rad etdi.",
            )
        except Exception:
            pass
        return {"outcome": "declined"}

    if not livekit_configured():
        return {"outcome": "livekit_missing"}

    room_id = f"room_{uuid.uuid4().hex[:12]}"
    async with async_session() as session:
        call = CallSession(user1_id=proposal["requester_id"], user2_id=proposal["candidate_id"], room_id=room_id)
        session.add(call)
        me = await session.get(User, user_id)
        other_user = await session.get(User, other["user_id"])
        if me:
            me.is_in_call = True
        if other_user:
            other_user.is_in_call = True
        # Ikkalasi ham qabul qilganda — sevimlilar + chat ochiladi
        await ensure_mutual_favorites_and_thread(session, user_id, other["user_id"])
        await session.commit()

    me_join = livekit_join_payload(identity=str(user_id), name=me.name if me else str(user_id), room_id=room_id)
    other_join = livekit_join_payload(
        identity=str(other["user_id"]),
        name=other_user.name if other_user else str(other["user_id"]),
        room_id=room_id,
    )

    await set_result(
        other["user_id"],
        "matched",
        room_id=room_id,
        partner_id=user_id,
        livekit_url=other_join["livekit_url"],
        livekit_token=other_join["livekit_token"],
    )
    await set_result(
        user_id,
        "matched",
        room_id=room_id,
        partner_id=other["user_id"],
        livekit_url=me_join["livekit_url"],
        livekit_token=me_join["livekit_token"],
    )

    await _notify_match_open(me, other_user.name if other_user else str(other["user_id"]))
    await _notify_match_open(other_user, me.name if me else str(user_id))
    await notify_admins(
        f"📞 Aloqa boshlandi\n"
        f"Xona: <code>{room_id}</code>\n"
        f"<code>{proposal['requester_id']}</code> ↔ <code>{proposal['candidate_id']}</code>\n"
        f"{(me.name if me else '?')} · {(other_user.name if other_user else '?')}"
    )

    return {
        "outcome": "matched",
        "room_id": room_id,
        "partner_id": other["user_id"],
        "livekit_url": me_join["livekit_url"],
        "livekit_token": me_join["livekit_token"],
    }
