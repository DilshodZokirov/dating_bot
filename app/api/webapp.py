import uuid

import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app import test_mode
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
    requeue_user,
    set_result,
)
from app.matching.respond import respond_to_proposal
from app.matching.age_brackets import age_range_options, clamp_prefer
from app.livekit_tokens import livekit_configured, livekit_join_payload
from app.models import (
    CallSession,
    Gender,
    Language,
    LookingFor,
    ReportReason,
    SavedPartner,
    SearchScope,
    SessionStatus,
    User,
)
from app.moderation import add_block, add_report, get_banned_ids, get_blocked_ids, is_blocked_pair
from app.presence import is_online, online_map, touch_presence
from app.telegram_auth import InitDataError, validate_init_data
from app.telegram_client import notify_admins

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
        "prefer_age_min": getattr(user, "prefer_age_min", None) or settings.min_age,
        "prefer_age_max": getattr(user, "prefer_age_max", None) or 99,
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
        "prefer_age_min": proposal.get(f"{prefix}_prefer_age_min", 18),
        "prefer_age_max": proposal.get(f"{prefix}_prefer_age_max", 99),
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
        "prefer_age_min": getattr(user, "prefer_age_min", None) or settings.min_age,
        "prefer_age_max": getattr(user, "prefer_age_max", None) or 99,
        "is_banned": user.is_banned,
        "test_mode": test_mode.is_enabled(),
    }


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=100)
    language: Language | None = None
    city: str | None = Field(default=None, max_length=64)
    search_scope: SearchScope | None = None
    age: int | None = Field(default=None, ge=18, le=99)
    looking_for: LookingFor | None = None
    prefer_age_min: int | None = Field(default=None, ge=18, le=99)
    prefer_age_max: int | None = Field(default=None, ge=18, le=99)


@router.get("/cities")
async def get_cities():
    return {"cities": UZBEKISTAN_CITIES}


@router.get("/age-ranges")
async def get_age_ranges():
    return {"ranges": age_range_options(), "min_age": settings.min_age}


async def _build_ice_servers() -> dict:
    ice_servers: list[dict] = [{"urls": "stun:stun.l.google.com:19302"}]

    # 1) O'z TURN (coturn / static) — eng oddiy yo'l
    if settings.turn_urls and settings.turn_username and settings.turn_password:
        urls = [u.strip() for u in settings.turn_urls.split(",") if u.strip()]
        ice_servers.append(
            {
                "urls": urls if len(urls) > 1 else urls[0],
                "username": settings.turn_username,
                "credential": settings.turn_password,
            }
        )
        return {"iceServers": ice_servers}

    # 2) Metered.ca dinamik credential
    if not settings.metered_domain or not settings.metered_secret_key:
        return {"iceServers": ice_servers}

    base = f"https://{settings.metered_domain}/api/v1/turn"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            create_resp = await client.post(
                f"{base}/credential",
                params={"secretKey": settings.metered_secret_key},
                json={"expiryInSeconds": 3600, "label": "call"},
            )
            create_resp.raise_for_status()
            api_key = create_resp.json()["apiKey"]

            ice_resp = await client.get(f"{base}/credentials", params={"apiKey": api_key})
            ice_resp.raise_for_status()
            metered_servers = ice_resp.json()
        if isinstance(metered_servers, list) and metered_servers:
            return {"iceServers": metered_servers}
        return {"iceServers": ice_servers}
    except Exception as e:
        print(f"TURN credentials error: {e}")
        return {"iceServers": ice_servers}


@router.get("/turn-credentials")
async def get_turn_credentials(x_telegram_init_data: str | None = Header(default=None)):
    _auth(x_telegram_init_data)  # faqat ro'yxatdan o'tgan/haqiqiy Telegram foydalanuvchisi so'rasin
    return await _build_ice_servers()


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
        if update.age is not None:
            if update.age < settings.min_age:
                raise HTTPException(status_code=400, detail=f"Minimal yosh: {settings.min_age}")
            user.age = update.age
        if update.looking_for is not None:
            user.looking_for = update.looking_for
        if update.prefer_age_min is not None or update.prefer_age_max is not None:
            lo = update.prefer_age_min if update.prefer_age_min is not None else (user.prefer_age_min or settings.min_age)
            hi = update.prefer_age_max if update.prefer_age_max is not None else (user.prefer_age_max or 99)
            lo, hi = clamp_prefer(lo, hi, settings.min_age)
            user.prefer_age_min = lo
            user.prefer_age_max = hi

        await session.commit()

        # Sozlamalar o'zgarsa eski qidiruv yozuvini tozalash
        for lf in ("male", "female", "any"):
            await cancel_wait(user.id, lf)

    return {"status": "ok"}


@router.post("/search/start")
async def search_start(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    await touch_presence(int(tg_user["id"]))
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])

    if not user:
        raise HTTPException(status_code=400, detail="Avval botda /start orqali ro'yxatdan o'ting")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Hisobingiz cheklangan")

    exclude = await get_blocked_ids(user.id)
    exclude |= await get_banned_ids()
    exclude.add(user.id)

    candidate = await find_candidate(
        gender=user.gender.value,
        looking_for=user.looking_for.value,
        age=user.age,
        language=user.language.value,
        city=user.city,
        search_scope=user.search_scope.value,
        prefer_age_min=user.prefer_age_min or settings.min_age,
        prefer_age_max=user.prefer_age_max or 99,
        exclude_ids=exclude,
    )

    if not candidate:
        await join_queue(
            user.id, user.gender.value, user.looking_for.value, user.age,
            user.language.value, user.city, user.search_scope.value,
            user.prefer_age_min or settings.min_age, user.prefer_age_max or 99,
        )
        return {"status": "waiting"}

    async with async_session() as session:
        candidate_user = await session.get(User, candidate["user_id"])

    if not candidate_user or candidate_user.is_banned:
        await join_queue(
            user.id, user.gender.value, user.looking_for.value, user.age,
            user.language.value, user.city, user.search_scope.value,
            user.prefer_age_min or settings.min_age, user.prefer_age_max or 99,
        )
        return {"status": "waiting"}

    proposal_id = await create_mutual_proposal(requester=_queue_payload(user), candidate=candidate)

    # Taklif faqat Mini App polling orqali (Telegram xabar yo'q)
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
    await touch_presence(int(tg_user["id"]))
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
        # boshqa looking_for navbatlarida ham qolmasin
        for lf in ("male", "female", "any"):
            if lf != user.looking_for.value:
                await cancel_wait(user.id, lf)
        cancelled = await cancel_proposals_by_user(user.id)
        for proposal in cancelled:
            other = _other_side(proposal, user.id)
            await requeue_user(other)
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

    result = await respond_to_proposal(int(tg_user["id"]), payload.proposal_id, payload.decision)
    if result.get("outcome") == "livekit_missing":
        raise HTTPException(status_code=503, detail="LiveKit sozlanmagan")
    return result


class CallEndRequest(BaseModel):
    room_id: str
    partner_id: int


async def _end_call_session(room_id: str, notify_partner_id: int) -> None:
    async with async_session() as session:
        call = (
            await session.execute(select(CallSession).where(CallSession.room_id == room_id))
        ).scalar_one_or_none()
        if call:
            call.status = SessionStatus.ended
            call.ended_at = func.now()
            for uid in (call.user1_id, call.user2_id):
                user = await session.get(User, uid)
                if user:
                    user.is_in_call = False
            await session.commit()

    await set_result(notify_partner_id, "call_ended")


@router.post("/call/end")
async def call_end(payload: CallEndRequest, x_telegram_init_data: str | None = Header(default=None)):
    _auth(x_telegram_init_data)
    await _end_call_session(payload.room_id, payload.partner_id)
    return {"status": "ended"}


# ---------------------------------------------------------------------------
# Dev test mode — 1 Telegram akkaunt + kompyuter brauzeri
# ---------------------------------------------------------------------------

class TestCallEndRequest(BaseModel):
    room_id: str
    partner_id: int
    token: str


@router.post("/test/match")
async def test_match(x_telegram_init_data: str | None = Header(default=None)):
    if not test_mode.is_enabled():
        raise HTTPException(status_code=404, detail="Test mode o'chirilgan")

    tg_user = _auth(x_telegram_init_data)
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])
        if not user:
            raise HTTPException(status_code=400, detail="Avval botda /start orqali ro'yxatdan o'ting")
        if user.is_banned:
            raise HTTPException(status_code=403, detail="Hisobingiz cheklangan")

        # Opposite gender for realistic proposal UI (age rule: female younger)
        if user.gender == Gender.male:
            peer_gender = Gender.female
            peer_age = max(settings.min_age, user.age - 1)
        else:
            peer_gender = Gender.male
            peer_age = user.age + 1

        peer = await test_mode.ensure_test_peer(session, language=user.language)
        peer.name = test_mode.TEST_PEER_NAME
        peer.gender = peer_gender
        peer.age = peer_age
        peer.looking_for = LookingFor.any
        peer.language = user.language
        await session.commit()

        room_id = f"test_{uuid.uuid4().hex[:12]}"
        call = CallSession(user1_id=user.id, user2_id=peer.id, room_id=room_id)
        session.add(call)
        await session.commit()

    token = test_mode.create_test_token(room_id, user_id=test_mode.TEST_PEER_ID)
    base = (settings.webapp_url or "").rstrip("/")
    peer_path = f"/webapp/test-peer.html?token={token}&partner_id={user.id}"
    peer_url = f"{base}{peer_path}" if base else peer_path

    if not livekit_configured():
        raise HTTPException(status_code=503, detail="LiveKit sozlanmagan (.env ga LIVEKIT_* qo'shing)")

    me_join = livekit_join_payload(identity=str(user.id), name=user.name, room_id=room_id)

    return {
        "status": "matched",
        "room_id": room_id,
        "partner_id": test_mode.TEST_PEER_ID,
        "partner_name": test_mode.TEST_PEER_NAME,
        "test_token": token,
        "test_peer_url": peer_url,
        "test_peer_path": peer_path,
        "livekit_url": me_join["livekit_url"],
        "livekit_token": me_join["livekit_token"],
    }


@router.get("/test/livekit-token")
async def test_livekit_token(token: str):
    """Test peer (kompyuter) uchun LiveKit token."""
    if not test_mode.is_enabled():
        raise HTTPException(status_code=404, detail="Test mode o'chirilgan")
    try:
        claims = test_mode.verify_test_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    if not livekit_configured():
        raise HTTPException(status_code=503, detail="LiveKit sozlanmagan")
    join = livekit_join_payload(
        identity=str(test_mode.TEST_PEER_ID),
        name=test_mode.TEST_PEER_NAME,
        room_id=claims["room_id"],
    )
    return join


class LiveKitTokenRequest(BaseModel):
    room_id: str


@router.post("/livekit/token")
async def livekit_token(payload: LiveKitTokenRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    if not livekit_configured():
        raise HTTPException(status_code=503, detail="LiveKit sozlanmagan")
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])
        if not user:
            raise HTTPException(status_code=400, detail="Ro'yxatdan o'ting")
    return livekit_join_payload(identity=str(user.id), name=user.name, room_id=payload.room_id)


@router.get("/test/turn-credentials")
async def test_turn_credentials(token: str):
    if not test_mode.is_enabled():
        raise HTTPException(status_code=404, detail="Test mode o'chirilgan")
    try:
        test_mode.verify_test_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return await _build_ice_servers()


@router.post("/test/call/end")
async def test_call_end(payload: TestCallEndRequest):
    if not test_mode.is_enabled():
        raise HTTPException(status_code=404, detail="Test mode o'chirilgan")
    try:
        claims = test_mode.verify_test_token(payload.token, expected_room_id=payload.room_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Test peer only notifies the real Telegram user
    if claims["user_id"] != test_mode.TEST_PEER_ID:
        raise HTTPException(status_code=403, detail="faqat test peer")

    await _end_call_session(payload.room_id, payload.partner_id)
    return {"status": "ended"}


# ---------------------------------------------------------------------------
# Moderatsiya — bloklash / shikoyat
# ---------------------------------------------------------------------------

class BlockRequest(BaseModel):
    partner_id: int
    room_id: str | None = None


class ReportRequest(BaseModel):
    partner_id: int
    reason: ReportReason = ReportReason.other
    details: str | None = Field(default=None, max_length=500)
    room_id: str | None = None
    also_block: bool = True


@router.post("/block")
async def block_user(payload: BlockRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    if payload.partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizni bloklab bo'lmaydi")

    async with async_session() as session:
        me = await session.get(User, me_id)
        partner = await session.get(User, payload.partner_id)
    if not me:
        raise HTTPException(status_code=400, detail="Avval ro'yxatdan o'ting")
    if not partner:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    await add_block(me_id, payload.partner_id)
    if payload.room_id:
        await _end_call_session(payload.room_id, payload.partner_id)

    return {"status": "blocked", "partner_id": payload.partner_id}


@router.post("/report")
async def report_user(payload: ReportRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    if payload.partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizga shikoyat qilib bo'lmaydi")

    async with async_session() as session:
        me = await session.get(User, me_id)
        partner = await session.get(User, payload.partner_id)
    if not me:
        raise HTTPException(status_code=400, detail="Avval ro'yxatdan o'ting")
    if not partner:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    report = await add_report(
        reporter_id=me_id,
        reported_id=payload.partner_id,
        reason=payload.reason,
        details=payload.details,
        room_id=payload.room_id,
    )
    if payload.also_block:
        await add_block(me_id, payload.partner_id)
    if payload.room_id:
        await _end_call_session(payload.room_id, payload.partner_id)

    await notify_admins(
        f"🚨 Yangi shikoyat #{report.id}\n"
        f"Kim: <code>{me_id}</code> ({me.name})\n"
        f"Kimga: <code>{payload.partner_id}</code> ({partner.name})\n"
        f"Sabab: <b>{payload.reason.value}</b>\n"
        f"Xona: {payload.room_id or '—'}\n"
        f"Izoh: {(payload.details or '—')[:200]}\n\n"
        f"/ban {payload.partner_id} — ban\n"
        f"/reports — ochiq shikoyatlar"
    )

    return {
        "status": "reported",
        "report_id": report.id,
        "blocked": payload.also_block,
        "partner_id": payload.partner_id,
    }


# ---------------------------------------------------------------------------
# Presence + Saqlanganlar
# ---------------------------------------------------------------------------

@router.post("/presence/ping")
async def presence_ping(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    await touch_presence(int(tg_user["id"]))
    return {"status": "ok", "online": True}


class SavedRequest(BaseModel):
    partner_id: int


@router.get("/saved")
async def list_saved(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    await touch_presence(me_id)

    async with async_session() as session:
        rows = (
            await session.execute(
                select(SavedPartner, User)
                .join(User, User.id == SavedPartner.partner_id)
                .where(SavedPartner.user_id == me_id)
                .order_by(SavedPartner.id.desc())
            )
        ).all()

    partner_ids = [int(u.id) for _, u in rows]
    online = await online_map(partner_ids)

    items = []
    for saved, partner in rows:
        items.append({
            "partner_id": partner.id,
            "name": partner.name,
            "age": partner.age,
            "gender": partner.gender.value,
            "city": partner.city,
            "language": partner.language.value,
            "online": online.get(partner.id, False),
            "busy": bool(partner.is_in_call),
            "saved_at": saved.created_at.isoformat() if saved.created_at else None,
        })
    return {"items": items}


@router.post("/saved")
async def save_partner(payload: SavedRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    if payload.partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizni saqlab bo'lmaydi")
    if await is_blocked_pair(me_id, payload.partner_id):
        raise HTTPException(status_code=403, detail="Bloklangan juftlik")

    async with async_session() as session:
        me = await session.get(User, me_id)
        partner = await session.get(User, payload.partner_id)
        if not me or not partner:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        existing = (
            await session.execute(
                select(SavedPartner).where(
                    SavedPartner.user_id == me_id, SavedPartner.partner_id == payload.partner_id
                )
            )
        ).scalar_one_or_none()
        if not existing:
            session.add(SavedPartner(user_id=me_id, partner_id=payload.partner_id))
            await session.commit()

    return {"status": "saved", "partner_id": payload.partner_id}


@router.delete("/saved/{partner_id}")
async def unsave_partner(partner_id: int, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    async with async_session() as session:
        row = (
            await session.execute(
                select(SavedPartner).where(
                    SavedPartner.user_id == me_id, SavedPartner.partner_id == partner_id
                )
            )
        ).scalar_one_or_none()
        if row:
            await session.delete(row)
            await session.commit()
    return {"status": "removed", "partner_id": partner_id}


class InviteRequest(BaseModel):
    partner_id: int


@router.post("/saved/invite")
async def invite_saved(payload: InviteRequest, x_telegram_init_data: str | None = Header(default=None)):
    """Saqlangan online suhbatdoshni suhbatga chaqirish (faqat Mini App)."""
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    await touch_presence(me_id)

    if payload.partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizni chaqirib bo'lmaydi")
    if await is_blocked_pair(me_id, payload.partner_id):
        raise HTTPException(status_code=403, detail="Bloklangan juftlik")

    async with async_session() as session:
        me = await session.get(User, me_id)
        partner = await session.get(User, payload.partner_id)
        saved = (
            await session.execute(
                select(SavedPartner).where(
                    SavedPartner.user_id == me_id, SavedPartner.partner_id == payload.partner_id
                )
            )
        ).scalar_one_or_none()

    if not me or not partner:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    if not saved:
        raise HTTPException(status_code=400, detail="Avval suhbatdoshni saqlang")
    if me.is_banned or partner.is_banned:
        raise HTTPException(status_code=403, detail="Hisob cheklangan")
    if partner.is_in_call:
        raise HTTPException(status_code=409, detail="Suhbatdosh band (qo'ng'iroqda)")
    if not await is_online(payload.partner_id):
        raise HTTPException(status_code=409, detail="Suhbatdosh hozir online emas")

    # Navbatdan chiqarib, to'g'ridan-to'g'ri taklif
    for lf in ("male", "female", "any"):
        await cancel_wait(me.id, lf)
        await cancel_wait(partner.id, lf)

    proposal_id = await create_mutual_proposal(
        requester=_queue_payload(me),
        candidate=_queue_payload(partner),
    )
    await set_result(
        me.id, "proposal", proposal_id=proposal_id,
        other_name=partner.name, other_age=partner.age, other_gender=partner.gender.value,
    )
    await set_result(
        partner.id, "proposal", proposal_id=proposal_id,
        other_name=me.name, other_age=me.age, other_gender=me.gender.value,
    )

    return {
        "status": "invited",
        "proposal_id": proposal_id,
        "partner_id": partner.id,
        "partner_online": True,
    }
