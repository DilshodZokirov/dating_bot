import uuid
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.avatars import (
    ALLOWED_TYPES,
    MAX_AVATAR_BYTES,
    avatar_url,
    delete_avatar_files,
    ensure_avatar_dir,
    find_avatar_file,
)
from app.cities import UZBEKISTAN_CITIES
from app.config import settings
from app.database import async_session
from app.matching.queue import (
    cancel_proposals_by_user,
    cancel_wait,
    count_compatible_waiters,
    create_mutual_proposal,
    find_candidate,
    join_queue,
    pop_result,
    requeue_user,
    set_result,
    SAVED_INVITE_TTL_SECONDS,
)
from app.matching.respond import respond_to_proposal
from app.matching.age_brackets import clamp_prefer, prefer_bounds_meta
from app.livekit_tokens import livekit_configured, livekit_join_payload
from app.chat_service import (
    ensure_mutual_favorites_and_thread,
    get_thread_for_pair,
    thread_partner_id,
    user_threads,
)
from app.models import (
    CallFeedback,
    CallSession,
    ChatInvite,
    ChatInviteStatus,
    ChatMessage,
    ChatThread,
    Language,
    LookingFor,
    PhoneShareRequest,
    PhoneShareStatus,
    Report,
    ReportReason,
    ReportStatus,
    SavedPartner,
    SearchScope,
    SessionStatus,
    User,
)
from app.moderation import (
    add_block,
    add_report,
    get_banned_ids,
    get_blocked_ids,
    is_blocked_pair,
    mark_report,
    set_user_banned,
)
from app.presence import is_online, online_map, touch_presence
from app.telegram_auth import InitDataError, validate_init_data
from app.phone_share import accept_phone_share, decline_phone_share
from app.telegram_client import (
    notify_admins,
    phone_request_keyboard,
    proposal_keyboard,
    send_message,
)
from app.topics import DEFAULT_TOPIC, LEGACY_TOPIC_MAP, MATCH_TOPICS, TOPIC_IDS, normalize_topic
from app.i18n import t, gender_label

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
        "prefer_age_min": user.prefer_age_min if user.prefer_age_min is not None else 12,
        "prefer_age_max": user.prefer_age_max if user.prefer_age_max is not None else 100,
        "match_topic": normalize_topic(getattr(user, "match_topic", None)),
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
        "prefer_age_min": proposal.get(f"{prefix}_prefer_age_min", 12),
        "prefer_age_max": proposal.get(f"{prefix}_prefer_age_max", 100),
        "match_topic": normalize_topic(proposal.get(f"{prefix}_match_topic", "any")),
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
        "id": user.id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender.value,
        "looking_for": user.looking_for.value,
        "language": user.language.value,
        "ui_language": (
            user.ui_language.value
            if getattr(user, "ui_language", None) is not None
            else user.language.value
        ),
        "bio": user.bio,
        "location": user.location,
        "city": user.city,
        "search_scope": user.search_scope.value,
        "prefer_age_min": user.prefer_age_min if user.prefer_age_min is not None else settings.min_age,
        "prefer_age_max": user.prefer_age_max if user.prefer_age_max is not None else 100,
        "is_banned": user.is_banned,
        "is_admin": int(user.id) in settings.admin_id_set(),
        "has_avatar": bool(getattr(user, "has_avatar", False)),
        "avatar_url": avatar_url(user.id, bool(getattr(user, "has_avatar", False))),
        "match_topic": normalize_topic(getattr(user, "match_topic", None)),
    }


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None, max_length=300)
    location: str | None = Field(default=None, max_length=100)
    language: Language | None = None  # suhbat / matching tili
    ui_language: Language | None = None  # dastur (UI) tili
    city: str | None = Field(default=None, max_length=64)
    search_scope: SearchScope | None = None
    age: int | None = Field(default=None, ge=12, le=100)
    looking_for: LookingFor | None = None
    prefer_age_min: int | None = Field(default=None, ge=0, le=100)
    prefer_age_max: int | None = Field(default=None, ge=0, le=100)
    match_topic: str | None = Field(default=None, max_length=32)


@router.get("/cities")
async def get_cities():
    return {"cities": UZBEKISTAN_CITIES}


@router.get("/age-ranges")
async def get_age_ranges():
    meta = prefer_bounds_meta(settings.min_age)
    return {"ranges": [], **meta}


@router.get("/topics")
async def get_topics():
    return {"topics": MATCH_TOPICS, "default": DEFAULT_TOPIC}


# Matching shu til bo'yicha filtrlaydi (queue: language == language)
LANGUAGES = [
    {"id": "uz", "label": "O‘zbek"},
    {"id": "ru", "label": "Русский"},
    {"id": "en", "label": "English"},
    {"id": "de", "label": "Deutsch"},
    {"id": "tg", "label": "Tojik"},
    {"id": "tr", "label": "Türkçe"},
    {"id": "ko", "label": "한국어"},
    {"id": "ja", "label": "日本語"},
    {"id": "zh", "label": "中文"},
    {"id": "ar", "label": "العربية"},
]


@router.get("/languages")
async def get_languages():
    return {"languages": LANGUAGES}


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
        if update.ui_language is not None:
            user.ui_language = update.ui_language
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
            lo = update.prefer_age_min if update.prefer_age_min is not None else (
                user.prefer_age_min if user.prefer_age_min is not None else 12
            )
            hi = update.prefer_age_max if update.prefer_age_max is not None else (
                user.prefer_age_max if user.prefer_age_max is not None else 100
            )
            lo, hi = clamp_prefer(lo, hi, settings.min_age)
            user.prefer_age_min = lo
            user.prefer_age_max = hi
        if update.match_topic is not None:
            raw = update.match_topic.strip()
            if raw not in TOPIC_IDS and raw not in LEGACY_TOPIC_MAP:
                raise HTTPException(status_code=400, detail="Noto'g'ri mavzu")
            user.match_topic = normalize_topic(raw)

        await session.commit()

        # Sozlamalar o'zgarsa eski qidiruv yozuvini tozalash
        for lf in ("male", "female", "any"):
            await cancel_wait(user.id, lf)

    return {"status": "ok"}


@router.post("/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    uid = int(tg_user["id"])
    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Faqat JPG, PNG yoki WEBP")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bo'sh fayl")
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=400, detail="Rasm 2 MB dan oshmasin")

    ext = ALLOWED_TYPES[content_type]
    ensure_avatar_dir()
    delete_avatar_files(uid)
    path = ensure_avatar_dir() / f"{uid}{ext}"
    path.write_bytes(data)

    async with async_session() as session:
        user = await session.get(User, uid)
        if not user:
            path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Avval ro'yxatdan o'ting")
        user.has_avatar = True
        await session.commit()

    return {"status": "ok", "avatar_url": avatar_url(uid, True)}


@router.delete("/profile/avatar")
async def remove_avatar(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    uid = int(tg_user["id"])
    delete_avatar_files(uid)
    async with async_session() as session:
        user = await session.get(User, uid)
        if user:
            user.has_avatar = False
            await session.commit()
    return {"status": "removed", "avatar_url": None}


@router.get("/avatar/{user_id}")
async def get_avatar(user_id: int):
    """Profil rasmi — <img src> uchun (auth header'siz)."""
    path = find_avatar_file(user_id)
    if not path:
        raise HTTPException(status_code=404, detail="Avatar yo'q")
    media = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "application/octet-stream")
    return FileResponse(path, media_type=media, headers={"Cache-Control": "public, max-age=3600"})


async def _compatible_pool_count(user: User) -> int:
    exclude = await get_blocked_ids(user.id)
    exclude |= await get_banned_ids()
    exclude.add(user.id)
    return await count_compatible_waiters(
        gender=user.gender.value,
        looking_for=user.looking_for.value,
        age=user.age,
        language=user.language.value,
        city=user.city,
        search_scope=user.search_scope.value,
        prefer_age_min=user.prefer_age_min if user.prefer_age_min is not None else 12,
        prefer_age_max=user.prefer_age_max if user.prefer_age_max is not None else 100,
        match_topic=normalize_topic(getattr(user, "match_topic", None)),
        exclude_ids=exclude,
    )


@router.get("/search/pool")
async def search_pool(x_telegram_init_data: str | None = Header(default=None)):
    """Sozlamalaringizga mos, hozir qidirayotgan odamlar soni."""
    tg_user = _auth(x_telegram_init_data)
    async with async_session() as session:
        user = await session.get(User, tg_user["id"])
    if not user:
        raise HTTPException(status_code=400, detail="Avval botda /start orqali ro'yxatdan o'ting")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Hisobingiz cheklangan")
    count = await _compatible_pool_count(user)
    return {"count": count}


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

    # Eski navbat/takliflarni tozalab, yangi qidiruv
    for lf in ("male", "female", "any"):
        await cancel_wait(user.id, lf)

    proposal = await _try_create_proposal(user)
    if proposal:
        return {"status": "proposal_sent"}

    await join_queue(
        user.id, user.gender.value, user.looking_for.value, user.age,
        user.language.value, user.city, user.search_scope.value,
        user.prefer_age_min if user.prefer_age_min is not None else 12,
        user.prefer_age_max if user.prefer_age_max is not None else 100,
        normalize_topic(getattr(user, "match_topic", None)),
    )

    # Ikkalasi bir vaqtda bosganda: men navbatga tushganimdan keyin yana bir marta
    proposal = await _try_create_proposal(user, leave_queue_if_matched=True)
    if proposal:
        return {"status": "proposal_sent"}

    return {"status": "waiting"}


@router.get("/search/status")
async def search_status(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    uid = int(tg_user["id"])
    await touch_presence(uid)

    result = await pop_result(uid)
    if result:
        return result

    # Navbatda kutayotganda qayta match — ikkala akkaunt birga qidirganda tiqilib qolmasin
    async with async_session() as session:
        user = await session.get(User, uid)
    if user and not user.is_banned:
        proposal = await _try_create_proposal(user, leave_queue_if_matched=True)
        if proposal:
            # set_result o'zimizga ham yozilgan — shu poll javobida qaytaramiz, dublikat bo'lmasin
            await pop_result(uid)
            return proposal

    count = 0
    if user and not user.is_banned:
        try:
            count = await _compatible_pool_count(user)
        except Exception:
            count = 0
    return {"outcome": "waiting", "compatible_count": count}


async def _try_create_proposal(user: User, leave_queue_if_matched: bool = False) -> dict | None:
    """
    Navbatdan mos kandidat topsa — ikkalasiga proposal result yozadi.
    Qaytaradi: polling uchun proposal dict yoki None.
    """
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
        prefer_age_min=user.prefer_age_min if user.prefer_age_min is not None else 12,
        prefer_age_max=user.prefer_age_max if user.prefer_age_max is not None else 100,
        match_topic=normalize_topic(getattr(user, "match_topic", None)),
        exclude_ids=exclude,
    )
    if not candidate:
        return None

    async with async_session() as session:
        candidate_user = await session.get(User, candidate["user_id"])

    if not candidate_user or candidate_user.is_banned:
        # Kandidat yaroqsiz — qayta navbatga qo'ymaymiz (banned)
        return None

    if leave_queue_if_matched:
        for lf in ("male", "female", "any"):
            await cancel_wait(user.id, lf)

    proposal_id = await create_mutual_proposal(requester=_queue_payload(user), candidate=candidate)

    await set_result(
        user.id, "proposal", proposal_id=proposal_id,
        other_id=candidate_user.id,
        other_name=candidate_user.name, other_age=candidate_user.age, other_gender=candidate_user.gender.value,
        other_avatar_url=avatar_url(candidate_user.id, bool(getattr(candidate_user, "has_avatar", False))),
    )
    await set_result(
        candidate["user_id"], "proposal", proposal_id=proposal_id,
        other_id=user.id,
        other_name=user.name, other_age=user.age, other_gender=user.gender.value,
        other_avatar_url=avatar_url(user.id, bool(getattr(user, "has_avatar", False))),
    )

    return {
        "outcome": "proposal",
        "proposal_id": proposal_id,
        "other_id": candidate_user.id,
        "other_name": candidate_user.name,
        "other_age": candidate_user.age,
        "other_gender": candidate_user.gender.value,
        "other_avatar_url": avatar_url(candidate_user.id, bool(getattr(candidate_user, "has_avatar", False))),
    }


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
        threads = await user_threads(session, me_id)
        thread_by_partner: dict[int, int] = {}
        for th in threads:
            pid = await thread_partner_id(th, me_id)
            if pid is not None:
                thread_by_partner[int(pid)] = int(th.id)
        mutual_ids: set[int] = set()
        if partner_ids:
            mutual_rows = (
                await session.execute(
                    select(SavedPartner.user_id).where(
                        SavedPartner.partner_id == me_id,
                        SavedPartner.user_id.in_(partner_ids),
                    )
                )
            ).scalars().all()
            mutual_ids = {int(x) for x in mutual_rows}

    online = await online_map(partner_ids)

    items = []
    for saved, partner in rows:
        pid = int(partner.id)
        items.append({
            "partner_id": partner.id,
            "name": partner.name,
            "age": partner.age,
            "gender": partner.gender.value,
            "city": partner.city,
            "language": partner.language.value,
            "online": online.get(partner.id, False),
            "busy": bool(partner.is_in_call),
            "has_avatar": bool(getattr(partner, "has_avatar", False)),
            "avatar_url": avatar_url(partner.id, bool(getattr(partner, "has_avatar", False))),
            "saved_at": saved.created_at.isoformat() if saved.created_at else None,
            "mutual": pid in mutual_ids or pid in thread_by_partner,
            "can_chat": pid in thread_by_partner,
            "thread_id": thread_by_partner.get(pid),
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
    """Saqlangan suhbatdoshni video suhbatga chaqirish — botga xabar + rozilik."""
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
    if partner.is_in_call or me.is_in_call:
        raise HTTPException(status_code=409, detail="Suhbatdosh band (qo'ng'iroqda)")

    # Navbatdan chiqarib, to'g'ridan-to'g'ri taklif
    for lf in ("male", "female", "any"):
        await cancel_wait(me.id, lf)
        await cancel_wait(partner.id, lf)

    proposal_id = await create_mutual_proposal(
        requester=_queue_payload(me),
        candidate=_queue_payload(partner),
        ttl=SAVED_INVITE_TTL_SECONDS,
    )
    # Chaqiruvchi avtomatik rozilik — hamroh botda qabul qiladi
    await respond_to_proposal(me.id, proposal_id, "accepted")

    await set_result(
        me.id, "invite_sent",
        proposal_id=proposal_id,
        partner_id=partner.id,
        other_name=partner.name,
    )
    await set_result(
        partner.id, "proposal", proposal_id=proposal_id,
        other_id=me.id,
        other_name=me.name, other_age=me.age, other_gender=me.gender.value,
        other_avatar_url=avatar_url(me.id, bool(getattr(me, "has_avatar", False))),
    )

    partner_lang = (
        partner.ui_language.value
        if getattr(partner, "ui_language", None) is not None
        else partner.language.value
    )
    invite_text = t(
        partner_lang,
        "saved_call_invite",
        name=me.name,
        age=me.age,
        gender=gender_label(partner_lang, me.gender.value),
    )
    try:
        await send_message(
            partner.id,
            invite_text,
            reply_markup=proposal_keyboard(
                proposal_id,
                t(partner_lang, "btn_accept"),
                t(partner_lang, "btn_decline"),
                t(partner_lang, "menu_btn"),
            ),
        )
    except Exception as e:
        print(f"saved invite notify {partner.id}: {e}", flush=True)

    await notify_admins(
        f"⭐ Saqlanganlardan chaqiruv\n"
        f"Kim: <code>{me.id}</code> ({me.name})\n"
        f"Kimga: <code>{partner.id}</code> ({partner.name})\n"
        f"Taklif: <code>{proposal_id}</code>"
    )

    return {
        "status": "invited",
        "proposal_id": proposal_id,
        "partner_id": partner.id,
        "partner_online": await is_online(partner.id),
        "bot_notified": True,
    }


class FeedbackRequest(BaseModel):
    room_id: str
    partner_id: int
    stars: int = Field(ge=1, le=5)


@router.post("/call/feedback")
async def call_feedback(payload: FeedbackRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    if payload.partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizni baholab bo'lmaydi")

    async with async_session() as session:
        existing = (
            await session.execute(
                select(CallFeedback).where(
                    CallFeedback.room_id == payload.room_id,
                    CallFeedback.from_user_id == me_id,
                )
            )
        ).scalar_one_or_none()
        if existing:
            existing.stars = payload.stars
            existing.to_user_id = payload.partner_id
        else:
            session.add(
                CallFeedback(
                    room_id=payload.room_id,
                    from_user_id=me_id,
                    to_user_id=payload.partner_id,
                    stars=payload.stars,
                )
            )
        await session.commit()
    return {"status": "ok", "stars": payload.stars}


# ---------------------------------------------------------------------------
# Telefon raqam so‘rovi (qo‘ng‘iroq davomida)
# ---------------------------------------------------------------------------

class PhoneRequestBody(BaseModel):
    partner_id: int
    room_id: str


@router.post("/call/phone-request")
async def request_phone_share(payload: PhoneRequestBody, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    if payload.partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizdan so'rab bo'lmaydi")
    if await is_blocked_pair(me_id, payload.partner_id):
        raise HTTPException(status_code=403, detail="Bloklangan juftlik")

    async with async_session() as session:
        me = await session.get(User, me_id)
        partner = await session.get(User, payload.partner_id)
        if not me or not partner:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        call = (
            await session.execute(
                select(CallSession).where(
                    CallSession.room_id == payload.room_id,
                    CallSession.status == SessionStatus.active,
                )
            )
        ).scalar_one_or_none()
        if not call or me_id not in (call.user1_id, call.user2_id) or payload.partner_id not in (
            call.user1_id,
            call.user2_id,
        ):
            raise HTTPException(status_code=400, detail="Faol qo'ng'iroq topilmadi")

        existing = (
            await session.execute(
                select(PhoneShareRequest).where(
                    PhoneShareRequest.room_id == payload.room_id,
                    PhoneShareRequest.from_user_id == me_id,
                    PhoneShareRequest.to_user_id == payload.partner_id,
                    PhoneShareRequest.status == PhoneShareStatus.pending,
                )
            )
        ).scalar_one_or_none()
        if existing:
            return {"status": "pending", "request_id": existing.id}

        req = PhoneShareRequest(
            room_id=payload.room_id,
            from_user_id=me_id,
            to_user_id=payload.partner_id,
            status=PhoneShareStatus.pending,
        )
        session.add(req)
        await session.commit()
        await session.refresh(req)
        request_id = req.id
        me_name = me.name

    partner_lang = (
        partner.ui_language.value
        if getattr(partner, "ui_language", None) is not None
        else partner.language.value
    )
    try:
        await send_message(
            payload.partner_id,
            t(partner_lang, "phone_request_ask", name=me_name),
            reply_markup=phone_request_keyboard(
                request_id,
                t(partner_lang, "btn_accept"),
                t(partner_lang, "btn_decline"),
            ),
        )
    except Exception as e:
        print(f"phone request notify {payload.partner_id}: {e}", flush=True)

    return {"status": "pending", "request_id": request_id}


@router.get("/call/phone-incoming")
async def list_incoming_phone_requests(x_telegram_init_data: str | None = Header(default=None)):
    """Mini App ichida kelgan telefon so‘rovlari (ixtiyoriy UI)."""
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    async with async_session() as session:
        rows = (
            await session.execute(
                select(PhoneShareRequest, User)
                .join(User, User.id == PhoneShareRequest.from_user_id)
                .where(
                    PhoneShareRequest.to_user_id == me_id,
                    PhoneShareRequest.status == PhoneShareStatus.pending,
                )
                .order_by(PhoneShareRequest.id.desc())
            )
        ).all()
    return {
        "items": [
            {
                "request_id": req.id,
                "room_id": req.room_id,
                "from_user_id": req.from_user_id,
                "from_name": user.name,
            }
            for req, user in rows
        ]
    }


class PhoneRespondBody(BaseModel):
    action: str  # accept | decline


@router.post("/call/phone-request/{request_id}/respond")
async def respond_phone_share_api(
    request_id: int,
    payload: PhoneRespondBody,
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    action = (payload.action or "").strip().lower()
    if action not in ("accept", "decline"):
        raise HTTPException(status_code=400, detail="action: accept | decline")

    if action == "decline":
        result = await decline_phone_share(request_id, me_id)
    else:
        result = await accept_phone_share(request_id, me_id)

    if result.get("status") == "invalid":
        raise HTTPException(status_code=404, detail="So'rov topilmadi")
    if result.get("status") == "closed":
        raise HTTPException(status_code=409, detail="So'rov yopilgan")
    return result


# ---------------------------------------------------------------------------
# Sevimlilar chat (taklif → rozilik → thread)
# ---------------------------------------------------------------------------

def _require_admin(user_id: int) -> None:
    if user_id not in settings.admin_id_set():
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")


def _partner_card(user: User, online: bool = False) -> dict:
    return {
        "partner_id": user.id,
        "name": user.name,
        "age": user.age,
        "gender": user.gender.value,
        "city": user.city,
        "language": user.language.value,
        "online": online,
        "busy": bool(user.is_in_call),
        "has_avatar": bool(getattr(user, "has_avatar", False)),
        "avatar_url": avatar_url(user.id, bool(getattr(user, "has_avatar", False))),
    }


class ChatInviteCreate(BaseModel):
    partner_id: int


class ChatInviteRespond(BaseModel):
    action: str  # accept | decline


class ChatMessageCreate(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


@router.post("/chat/invite")
async def create_chat_invite(payload: ChatInviteCreate, x_telegram_init_data: str | None = Header(default=None)):
    """Sevimlilar / chatga taklif yuborish."""
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    partner_id = int(payload.partner_id)
    if partner_id == me_id:
        raise HTTPException(status_code=400, detail="O'zingizga taklif yuborib bo'lmaydi")
    if await is_blocked_pair(me_id, partner_id):
        raise HTTPException(status_code=403, detail="Bloklangan juftlik")

    async with async_session() as session:
        me = await session.get(User, me_id)
        partner = await session.get(User, partner_id)
        if not me or not partner:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
        if me.is_banned or partner.is_banned:
            raise HTTPException(status_code=403, detail="Hisob cheklangan")

        existing_thread = await get_thread_for_pair(session, me_id, partner_id)
        if existing_thread:
            return {
                "status": "already_friends",
                "thread_id": existing_thread.id,
                "partner_id": partner_id,
            }

        pending = (
            await session.execute(
                select(ChatInvite).where(
                    ChatInvite.from_user_id == me_id,
                    ChatInvite.to_user_id == partner_id,
                    ChatInvite.status == ChatInviteStatus.pending,
                )
            )
        ).scalar_one_or_none()
        if pending:
            return {"status": "pending", "invite_id": pending.id, "partner_id": partner_id}

        # Agar ular menga taklif yuborgan bo'lsa — avtomatik qabul
        reverse = (
            await session.execute(
                select(ChatInvite).where(
                    ChatInvite.from_user_id == partner_id,
                    ChatInvite.to_user_id == me_id,
                    ChatInvite.status == ChatInviteStatus.pending,
                )
            )
        ).scalar_one_or_none()
        if reverse:
            reverse.status = ChatInviteStatus.accepted
            reverse.responded_at = datetime.now(timezone.utc)
            thread = await ensure_mutual_favorites_and_thread(session, me_id, partner_id)
            await session.commit()
            try:
                await send_message(
                    partner_id,
                    f"✅ <b>{me.name}</b> sevimlilar taklifingizni qabul qildi. Mini App → Saqlangan → Chat.",
                )
            except Exception:
                pass
            return {
                "status": "accepted",
                "invite_id": reverse.id,
                "thread_id": thread.id,
                "partner_id": partner_id,
            }

        invite = ChatInvite(
            from_user_id=me_id,
            to_user_id=partner_id,
            status=ChatInviteStatus.pending,
        )
        session.add(invite)
        await session.commit()
        await session.refresh(invite)

    try:
        await send_message(
            partner_id,
            f"⭐ <b>{me.name}</b> sizni sevimlilarga taklif qildi.\n"
            f"Mini App → Saqlangan bo‘limida qabul qilishingiz mumkin.",
        )
    except Exception:
        pass

    return {"status": "pending", "invite_id": invite.id, "partner_id": partner_id}


@router.get("/chat/invites")
async def list_chat_invites(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    await touch_presence(me_id)

    async with async_session() as session:
        incoming_rows = (
            await session.execute(
                select(ChatInvite, User)
                .join(User, User.id == ChatInvite.from_user_id)
                .where(
                    ChatInvite.to_user_id == me_id,
                    ChatInvite.status == ChatInviteStatus.pending,
                )
                .order_by(ChatInvite.id.desc())
            )
        ).all()
        outgoing_rows = (
            await session.execute(
                select(ChatInvite, User)
                .join(User, User.id == ChatInvite.to_user_id)
                .where(
                    ChatInvite.from_user_id == me_id,
                    ChatInvite.status == ChatInviteStatus.pending,
                )
                .order_by(ChatInvite.id.desc())
            )
        ).all()

    incoming_ids = [int(u.id) for _, u in incoming_rows]
    outgoing_ids = [int(u.id) for _, u in outgoing_rows]
    online = await online_map(incoming_ids + outgoing_ids)

    return {
        "incoming": [
            {
                "invite_id": inv.id,
                "from_user_id": inv.from_user_id,
                **_partner_card(user, online.get(user.id, False)),
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
            for inv, user in incoming_rows
        ],
        "outgoing": [
            {
                "invite_id": inv.id,
                "to_user_id": inv.to_user_id,
                **_partner_card(user, online.get(user.id, False)),
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
            for inv, user in outgoing_rows
        ],
    }


@router.post("/chat/invite/{invite_id}/respond")
async def respond_chat_invite(
    invite_id: int,
    payload: ChatInviteRespond,
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    action = (payload.action or "").strip().lower()
    if action not in ("accept", "decline"):
        raise HTTPException(status_code=400, detail="action: accept | decline")

    async with async_session() as session:
        invite = await session.get(ChatInvite, invite_id)
        if not invite or invite.to_user_id != me_id:
            raise HTTPException(status_code=404, detail="Taklif topilmadi")
        if invite.status != ChatInviteStatus.pending:
            raise HTTPException(status_code=409, detail="Taklif allaqachon yopilgan")

        me = await session.get(User, me_id)
        from_user = await session.get(User, invite.from_user_id)
        if not me or not from_user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        invite.responded_at = datetime.now(timezone.utc)
        if action == "decline":
            invite.status = ChatInviteStatus.declined
            await session.commit()
            return {"status": "declined", "invite_id": invite_id}

        invite.status = ChatInviteStatus.accepted
        thread = await ensure_mutual_favorites_and_thread(session, me_id, invite.from_user_id)
        await session.commit()
        thread_id = thread.id
        from_id = invite.from_user_id
        me_name = me.name

    try:
        await send_message(
            from_id,
            f"✅ <b>{me_name}</b> sevimlilar taklifingizni qabul qildi. Mini App → Saqlangan → Chat.",
        )
    except Exception:
        pass

    return {
        "status": "accepted",
        "invite_id": invite_id,
        "thread_id": thread_id,
        "partner_id": from_id,
    }


@router.get("/chat/threads")
async def list_chat_threads(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    await touch_presence(me_id)

    async with async_session() as session:
        threads = await user_threads(session, me_id)
        items = []
        partner_ids: list[int] = []
        for th in threads:
            pid = await thread_partner_id(th, me_id)
            if pid is None:
                continue
            partner = await session.get(User, pid)
            if not partner:
                continue
            last = (
                await session.execute(
                    select(ChatMessage)
                    .where(ChatMessage.thread_id == th.id)
                    .order_by(ChatMessage.id.desc())
                    .limit(1)
                )
            ).scalar_one_or_none()
            partner_ids.append(pid)
            items.append({
                "thread_id": th.id,
                "partner": _partner_card(partner),
                "last_message": (
                    {
                        "id": last.id,
                        "sender_id": last.sender_id,
                        "text": last.body,
                        "created_at": last.created_at.isoformat() if last.created_at else None,
                        "mine": last.sender_id == me_id,
                    }
                    if last
                    else None
                ),
                "updated_at": th.updated_at.isoformat() if th.updated_at else None,
            })

    online = await online_map(partner_ids)
    for it in items:
        pid = it["partner"]["partner_id"]
        it["partner"]["online"] = online.get(pid, False)

    return {"items": items}


@router.get("/chat/threads/{thread_id}/messages")
async def list_chat_messages(
    thread_id: int,
    after_id: int = 0,
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    await touch_presence(me_id)

    async with async_session() as session:
        thread = await session.get(ChatThread, thread_id)
        if not thread or me_id not in (thread.user_a_id, thread.user_b_id):
            raise HTTPException(status_code=404, detail="Chat topilmadi")
        q = select(ChatMessage).where(ChatMessage.thread_id == thread_id)
        if after_id > 0:
            q = q.where(ChatMessage.id > after_id)
        q = q.order_by(ChatMessage.id.asc()).limit(100)
        msgs = list((await session.execute(q)).scalars().all())
        pid = await thread_partner_id(thread, me_id)
        partner = await session.get(User, pid) if pid else None

    return {
        "thread_id": thread_id,
        "partner": _partner_card(partner) if partner else None,
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "text": m.body,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "mine": m.sender_id == me_id,
            }
            for m in msgs
        ],
    }


@router.post("/chat/threads/{thread_id}/messages")
async def send_chat_message(
    thread_id: int,
    payload: ChatMessageCreate,
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    me_id = int(tg_user["id"])
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Xabar bo'sh")
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Xabar juda uzun")

    async with async_session() as session:
        thread = await session.get(ChatThread, thread_id)
        if not thread or me_id not in (thread.user_a_id, thread.user_b_id):
            raise HTTPException(status_code=404, detail="Chat topilmadi")
        me = await session.get(User, me_id)
        if not me or me.is_banned:
            raise HTTPException(status_code=403, detail="Hisob cheklangan")
        pid = await thread_partner_id(thread, me_id)
        if pid and await is_blocked_pair(me_id, pid):
            raise HTTPException(status_code=403, detail="Bloklangan juftlik")

        msg = ChatMessage(thread_id=thread_id, sender_id=me_id, body=text[:1000])
        session.add(msg)
        thread.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(msg)

    return {
        "status": "ok",
        "message": {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "text": msg.body,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
            "mine": True,
        },
    }


# ---------------------------------------------------------------------------
# Admin panel (Mini App)
# ---------------------------------------------------------------------------

class AdminBanRequest(BaseModel):
    user_id: int
    reason: str | None = Field(default=None, max_length=300)


class AdminUserIdRequest(BaseModel):
    user_id: int


@router.get("/admin/stats")
async def admin_stats(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))

    async with async_session() as session:
        users_count = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
        banned_count = (
            await session.execute(select(func.count()).select_from(User).where(User.is_banned.is_(True)))
        ).scalar() or 0
        open_reports = (
            await session.execute(
                select(func.count()).select_from(Report).where(Report.status == ReportStatus.open)
            )
        ).scalar() or 0
        active_calls = (
            await session.execute(
                select(func.count()).select_from(CallSession).where(CallSession.status == SessionStatus.active)
            )
        ).scalar() or 0
        threads_count = (await session.execute(select(func.count()).select_from(ChatThread))).scalar() or 0

    return {
        "users": users_count,
        "banned": banned_count,
        "open_reports": open_reports,
        "active_calls": active_calls,
        "chat_threads": threads_count,
    }


@router.get("/admin/reports")
async def admin_list_reports(
    status: str = "open",
    limit: int = 30,
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))
    limit = max(1, min(limit, 100))

    status_map = {
        "open": ReportStatus.open,
        "reviewed": ReportStatus.reviewed,
        "dismissed": ReportStatus.dismissed,
        "all": None,
    }
    if status not in status_map:
        raise HTTPException(status_code=400, detail="status: open|reviewed|dismissed|all")

    async with async_session() as session:
        q = select(Report).order_by(Report.id.desc()).limit(limit)
        st = status_map[status]
        if st is not None:
            q = q.where(Report.status == st)
        reports = list((await session.execute(q)).scalars().all())
        items = []
        for r in reports:
            reporter = await session.get(User, r.reporter_id)
            reported = await session.get(User, r.reported_id)
            items.append({
                "id": r.id,
                "reason": r.reason.value,
                "details": r.details,
                "status": r.status.value,
                "room_id": r.room_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "reporter": {
                    "id": r.reporter_id,
                    "name": reporter.name if reporter else "—",
                    "is_banned": bool(reporter.is_banned) if reporter else False,
                },
                "reported": {
                    "id": r.reported_id,
                    "name": reported.name if reported else "—",
                    "is_banned": bool(reported.is_banned) if reported else False,
                    "has_avatar": bool(getattr(reported, "has_avatar", False)) if reported else False,
                    "avatar_url": avatar_url(
                        r.reported_id, bool(getattr(reported, "has_avatar", False))
                    )
                    if reported
                    else None,
                },
            })
    return {"items": items}


@router.post("/admin/reports/{report_id}/resolve")
async def admin_resolve_report(report_id: int, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))
    report = await mark_report(report_id, ReportStatus.reviewed)
    if not report:
        raise HTTPException(status_code=404, detail="Shikoyat topilmadi")
    return {"status": "reviewed", "report_id": report.id}


@router.post("/admin/reports/{report_id}/dismiss")
async def admin_dismiss_report(report_id: int, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))
    report = await mark_report(report_id, ReportStatus.dismissed)
    if not report:
        raise HTTPException(status_code=404, detail="Shikoyat topilmadi")
    return {"status": "dismissed", "report_id": report.id}


@router.post("/admin/ban")
async def admin_ban(payload: AdminBanRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    admin_id = int(tg_user["id"])
    _require_admin(admin_id)
    if payload.user_id == admin_id:
        raise HTTPException(status_code=400, detail="O'zingizni ban qilib bo'lmaydi")
    user = await set_user_banned(payload.user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    await notify_admins(
        f"🚫 Admin <code>{admin_id}</code> ban qildi: <code>{user.id}</code> ({user.name})"
        + (f"\nSabab: {payload.reason}" if payload.reason else "")
    )
    return {"status": "banned", "user_id": user.id, "name": user.name}


@router.post("/admin/unban")
async def admin_unban(payload: AdminUserIdRequest, x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    admin_id = int(tg_user["id"])
    _require_admin(admin_id)
    user = await set_user_banned(payload.user_id, False)
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return {"status": "unbanned", "user_id": user.id, "name": user.name}


@router.get("/admin/users")
async def admin_search_users(
    q: str = "",
    limit: int = 20,
    x_telegram_init_data: str | None = Header(default=None),
):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))
    limit = max(1, min(limit, 50))
    query = (q or "").strip()

    async with async_session() as session:
        if query.isdigit():
            user = await session.get(User, int(query))
            users = [user] if user else []
        elif query:
            users = list(
                (
                    await session.execute(
                        select(User)
                        .where(User.name.ilike(f"%{query}%"))
                        .order_by(User.id.desc())
                        .limit(limit)
                    )
                ).scalars().all()
            )
        else:
            users = list(
                (
                    await session.execute(select(User).order_by(User.id.desc()).limit(limit))
                ).scalars().all()
            )

    return {
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "age": u.age,
                "gender": u.gender.value,
                "city": u.city,
                "language": u.language.value,
                "is_banned": bool(u.is_banned),
                "is_in_call": bool(u.is_in_call),
                "has_avatar": bool(getattr(u, "has_avatar", False)),
                "avatar_url": avatar_url(u.id, bool(getattr(u, "has_avatar", False))),
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
            if u
        ]
    }


@router.get("/admin/banned")
async def admin_banned_users(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))
    async with async_session() as session:
        users = list(
            (
                await session.execute(
                    select(User).where(User.is_banned.is_(True)).order_by(User.id.desc()).limit(100)
                )
            ).scalars().all()
        )
    return {
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "age": u.age,
                "city": u.city,
                "avatar_url": avatar_url(u.id, bool(getattr(u, "has_avatar", False))),
            }
            for u in users
        ]
    }


@router.get("/admin/calls")
async def admin_active_calls(x_telegram_init_data: str | None = Header(default=None)):
    tg_user = _auth(x_telegram_init_data)
    _require_admin(int(tg_user["id"]))
    async with async_session() as session:
        calls = list(
            (
                await session.execute(
                    select(CallSession)
                    .where(CallSession.status == SessionStatus.active)
                    .order_by(CallSession.id.desc())
                    .limit(50)
                )
            ).scalars().all()
        )
        items = []
        for c in calls:
            u1 = await session.get(User, c.user1_id)
            u2 = await session.get(User, c.user2_id)
            items.append({
                "id": c.id,
                "room_id": c.room_id,
                "started_at": c.started_at.isoformat() if c.started_at else None,
                "user1": {
                    "id": c.user1_id,
                    "name": u1.name if u1 else "—",
                    "phone": u1.phone if u1 else None,
                },
                "user2": {
                    "id": c.user2_id,
                    "name": u2.name if u2 else "—",
                    "phone": u2.phone if u2 else None,
                },
            })
    return {"items": items}
