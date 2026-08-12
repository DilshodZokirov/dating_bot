"""Taklifga javob — API va (ixtiyoriy) bot uchun umumiy. Xabarlar faqat Mini App orqali."""

from __future__ import annotations

import uuid

from app.database import async_session
from app.livekit_tokens import livekit_configured, livekit_join_payload
from app.matching.queue import requeue_user, set_decision, set_result
from app.models import CallSession, User


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
        "prefer_age_min": proposal.get(f"{prefix}_prefer_age_min", 18),
        "prefer_age_max": proposal.get(f"{prefix}_prefer_age_max", 99),
    }


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

    return {
        "outcome": "matched",
        "room_id": room_id,
        "partner_id": other["user_id"],
        "livekit_url": me_join["livekit_url"],
        "livekit_token": me_join["livekit_token"],
    }
