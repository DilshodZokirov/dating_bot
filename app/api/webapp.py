import uuid

import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func

from app.cities import UZBEKISTAN_CITIES
from app.config import settings
from app.database import async_session
from app.matching.queue import (
    cancel_proposals_by_user,
    cancel_wait,
    create_mutual_proposal,
    find_candidate,
    join_queue,
    pop_result,
    set_decision,
    set_result,
)
from app.models import CallSession, Language, SearchScope, SessionStatus, User
from app.telegram_auth import InitDataError, validate_init_data

router = APIRouter(prefix="/api")


def _auth(x_telegram_init_data: str | None) -> dict:
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="initData yuborilmagan")
    try:
        return validate_init_data(x_telegram_init_data)
    except InitDataError as e:
        raise HTTPException(status_code=401, detail=str(e))


def _queue_payload(user: User) -> dict:
    return {
        "user_id": user.id,
        "gender": user.gender.value,
        "looking_for": user.looking_for.value,
        "age": user.age,
        "language": user.language.value,
        "city": user.city,
        "search_scope": user.search_scope.value,
    }


def _other_side(proposal: dict, responder_id: int) -> dict:
    """Taklifdagi ikkinchi tomon (javob bergan kishi emas) ma'lumotlarini qaytaradi."""
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
    }


@router.get("/me")
async def get_me(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])

    if not user:
        return {"registered": False}

    return {
        "registered": True,
        "name": user.name,
        "age": user.age,
        "gender": user.gender.value,
        "looking_for": user.looking_for.value,
        "language": user.language.value,
        "bio": user.bio,
        "location": user.location,
        "city": user.city,
        "search_scope": user.search_scope.value,
        "is_banned": user.is_banned,
    }


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=100)
    language: Language | None = None
    city: str | None = Field(default=None, max_length=64)
    search_scope: SearchScope | None = None


@router.get("/cities")
async def get_cities():
    return {"cities": UZBEKISTAN_CITIES}


@router.get("/turn-credentials")
async def get_turn_credentials(x_telegram_init_data: str | None = Header(default=None)):
    _auth(x_telegram_init_data)  # faqat ro'yxatdan o'tgan/haqiqiy Telegram foydalanuvchisi so'rasin

    fallback = [{"urls": "stun:stun.l.google.com:19302"}]

    if not settings.metered_domain or not settings.metered_secret_key:
        return {"iceServers": fallback}

    base = f"https://{settings.metered_domain}/api/v1/turn"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            # 1-bosqich: SECRET_KEY bilan vaqtinchalik credential (username/password) yaratamiz
            create_resp = await client.post(
                f"{base}/credential",
                params={"secretKey": settings.metered_secret_key},
                json={"expiryInSeconds": 3600, "label": "call"},
            )
            create_resp.raise_for_status()
            api_key = create_resp.json()["apiKey"]

            # 2-bosqich: shu vaqtinchalik apiKey orqali haqiqiy iceServers ro'yxatini olamiz
            ice_resp = await client.get(f"{base}/credentials", params={"apiKey": api_key})
            ice_resp.raise_for_status()
            ice_servers = ice_resp.json()
        return {"iceServers": ice_servers}
    except Exception as e:
        # TURN xizmati javob bermasa ham, qo'ng'iroq hech bo'lmasa STUN bilan urinib ko'rsin
        print(f"TURN credentials error: {e}")
        return {"iceServers": fallback}


@router.post("/profile")
async def update_profile(update: ProfileUpdate, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])
        if not user:
            raise HTTPException(status_code=400, detail="Avval botda /start orqali ro'yxatdan o'ting")

        if update.name is not None:
            user.name = update.name.strip()[:64] or user.name
        if update.bio is not None:
            user.bio = update.bio.strip()[:300]
        if update.location is not None:
            user.location = update.location.strip()[:100]
        if update.language is not None:
            user.language = update.language
        if update.city is not None:
            user.city = update.city.strip()[:64] or None
        if update.search_scope is not None:
            user.search_scope = update.search_scope

        await session.commit()

    return {"status": "ok"}


@router.post("/search/start")
async def search_start(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])

    if not user:
        raise HTTPException(status_code=400, detail="Avval botda /start orqali ro'yxatdan o'ting")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Hisobingiz cheklangan")

    candidate = await find_candidate(
        gender=user.gender.value,
        looking_for=user.looking_for.value,
        age=user.age,
        language=user.language.value,
        city=user.city,
        search_scope=user.search_scope.value,
    )

    if not candidate:
        await join_queue(
            user.id, user.gender.value, user.looking_for.value, user.age,
            user.language.value, user.city, user.search_scope.value,
        )
        return {"status": "waiting"}

    async with async_session() as session:
        candidate_user = await session.get(User, candidate["user_id"])

    proposal_id = await create_mutual_proposal(requester=_queue_payload(user), candidate=candidate)

    # Ikkalasiga ham — so'rovchiga HAM, kandidatga HAM — Mini App ichida ko'rsatiladigan
    # taklif natijasini yozamiz (Telegram chatiga xabar YUBORILMAYDI).
    await set_result(
        user.id, "proposal", proposal_id=proposal_id,
        other_name=candidate_user.name, other_age=candidate_user.age, other_gender=candidate_user.gender.value,
    )
    await set_result(
        candidate["user_id"], "proposal", proposal_id=proposal_id,
        other_name=user.name, other_age=user.age, other_gender=user.gender.value,
    )

    return {"status": "proposal_sent"}


@router.get("/search/status")
async def search_status(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    result = await pop_result(tg_user["id"])
    if result:
        return result
    return {"outcome": "waiting"}


@router.post("/search/cancel")
async def search_cancel(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])

    if user:
        await cancel_wait(user.id, user.looking_for.value)
        cancelled = await cancel_proposals_by_user(user.id)
        for proposal in cancelled:
            other = _other_side(proposal, user.id)
            await set_result(other["user_id"], "requeued")

    return {"status": "cancelled"}


class ProposalResponse(BaseModel):
    proposal_id: str
    decision: str  # "accepted" | "declined"


@router.post("/proposal/respond")
async def proposal_respond(payload: ProposalResponse, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    if payload.decision not in ("accepted", "declined"):
        raise HTTPException(status_code=400, detail="decision noto'g'ri")

    result = await set_decision(payload.proposal_id, tg_user["id"], payload.decision)

    if result["status"] == "invalid":
        return {"outcome": "invalid"}

    if result["status"] == "waiting_partner":
        return {"outcome": "waiting_partner"}

    proposal = result["proposal"]
    other = _other_side(proposal, tg_user["id"])

    if result["status"] == "declined":
        # boshqa tomonni avtomatik ravishda qayta qidiruvga qo'shamiz
        await join_queue(
            other["user_id"], other["gender"], other["looking_for"], other["age"],
            other["language"], other["city"], other["search_scope"],
        )
        await set_result(other["user_id"], "requeued")
        return {"outcome": "declined"}

    # status == "matched"
    room_id = f"room_{uuid.uuid4().hex[:12]}"
    async with async_session() as session:
        call = CallSession(user1_id=proposal["requester_id"], user2_id=proposal["candidate_id"], room_id=room_id)
        session.add(call)
        await session.commit()

    await set_result(other["user_id"], "matched", room_id=room_id, partner_id=tg_user["id"])
    return {"outcome": "matched", "room_id": room_id, "partner_id": other["user_id"]}


class CallEndRequest(BaseModel):
    room_id: str
    partner_id: int


@router.post("/call/end")
async def call_end(payload: CallEndRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)

    async with async_session() as session:
        result = await session.execute(
            CallSession.__table__.select().where(CallSession.room_id == payload.room_id)
        )
        row = result.first()
        if row:
            await session.execute(
                CallSession.__table__.update()
                .where(CallSession.room_id == payload.room_id)
                .values(status=SessionStatus.ended, ended_at=func.now())
            )
            await session.commit()

    await set_result(payload.partner_id, "call_ended")
    return {"status": "ended"}
