"""
Matching queue — Redis orqali.

Oqim (ikki tomonlama rozilik / mutual double opt-in):
1. Foydalanuvchi qidiruvni boshlaganda, navbatda mos kandidat qidiriladi
   (bir xil yosh oralig'i + bir xil til bo'yicha).
2. Kandidat topilsa — ikkalasiga HAM ("so'rovchi" va "kandidat") bir-birining
   profili bilan taklif yuboriladi: "Shu kishi bilan suhbatlashishga rozimisiz?"
3. Ikkalasi ham "Roziman" desagina suhbat (CallSession) yaratiladi.
4. Agar kimdir "Yo'q" desa — ikkinchi tomon avtomatik ravishda qayta
   qidiruv navbatiga qo'shiladi (davom etadi).
5. Mos kandidat topilmasa, foydalanuvchi navbatga qo'shiladi va kutadi.
"""

import json
import uuid

import redis.asyncio as redis

from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

LOCK_KEY = "matching:lock"
LOCK_TTL_MS = 5000

PROPOSAL_TTL_SECONDS = 120
RESULT_TTL_SECONDS = 180


def _queue_key(looking_for: str) -> str:
    return f"matching:queue:{looking_for}"


async def _acquire_lock() -> str:
    token = str(uuid.uuid4())
    while True:
        ok = await redis_client.set(LOCK_KEY, token, nx=True, px=LOCK_TTL_MS)
        if ok:
            return token


async def _release_lock(token: str):
    current = await redis_client.get(LOCK_KEY)
    if current == token:
        await redis_client.delete(LOCK_KEY)


# ---------------------------------------------------------------------------
# Navbat
# ---------------------------------------------------------------------------

def _age_compatible(gender_a: str, age_a: int, gender_b: str, age_b: int) -> bool:
    """
    Qoida: qiz bolaning yoshi yigitning yoshidan kichik bo'lishi kerak.
    """
    if gender_a == "male" and gender_b == "female":
        return age_b < age_a
    if gender_a == "female" and gender_b == "male":
        return age_a < age_b
    return True


def _city_compatible(a_city: str | None, a_scope: str, b_city: str | None, b_scope: str) -> bool:
    """
    Ikkala tomon ham bir-birining shahar afzalligiga hurmat qiladi:
    - Agar A faqat o'z shahri bo'yicha qidirsa (va shahri belgilangan bo'lsa),
      B ham xuddi shu shaharda bo'lishi kerak — aks holda mos emas.
    - Xuddi shu qoida B uchun ham amal qiladi.
    """
    if a_scope == "city" and a_city and a_city != b_city:
        return False
    if b_scope == "city" and b_city and b_city != a_city:
        return False
    return True


async def find_candidate(gender: str, looking_for: str, age: int, language: str,
                          city: str | None, search_scope: str) -> dict | None:
    """
    Navbatdan mos kandidatni qidiradi (yosh qoidasi: qiz yigitdan kichik + bir xil til +
    shahar afzalligi) va topilsa navbatdan olib tashlaydi. Topilmasa None qaytaradi.
    """
    token = await _acquire_lock()
    try:
        opposite_queue = _queue_key(gender)  # bizning gender'imizni qidirayotganlar shu navbatda
        raw_candidates = await redis_client.lrange(opposite_queue, 0, -1)
        for raw in raw_candidates:
            candidate = json.loads(raw)
            if not _age_compatible(gender, age, candidate["gender"], candidate["age"]):
                continue
            if candidate.get("language") != language:
                continue
            if not _city_compatible(city, search_scope, candidate.get("city"), candidate.get("search_scope", "country")):
                continue
            if looking_for != "any" and candidate["gender"] != looking_for:
                continue
            if candidate["looking_for"] != "any" and candidate["looking_for"] != gender:
                continue

            await redis_client.lrem(opposite_queue, 1, raw)
            return candidate
        return None
    finally:
        await _release_lock(token)


async def join_queue(user_id: int, gender: str, looking_for: str, age: int, language: str,
                      city: str | None, search_scope: str):
    my_queue = _queue_key(looking_for)
    payload = json.dumps({
        "user_id": user_id,
        "gender": gender,
        "looking_for": looking_for,
        "age": age,
        "language": language,
        "city": city,
        "search_scope": search_scope,
    })
    await redis_client.rpush(my_queue, payload)


async def cancel_wait(user_id: int, looking_for: str):
    """Foydalanuvchi qidiruvni bekor qilsa, navbatdan chiqarib tashlaymiz."""
    my_queue = _queue_key(looking_for)
    raw_candidates = await redis_client.lrange(my_queue, 0, -1)
    for raw in raw_candidates:
        candidate = json.loads(raw)
        if candidate["user_id"] == user_id:
            await redis_client.lrem(my_queue, 1, raw)
            break


# ---------------------------------------------------------------------------
# O'zaro taklif (mutual proposal) — ikkala tomon ham rozi bo'lishi kerak
# ---------------------------------------------------------------------------

def _proposal_key(proposal_id: str) -> str:
    return f"matching:proposal:{proposal_id}"


async def create_mutual_proposal(requester: dict, candidate: dict) -> str:
    """
    requester va candidate — {"user_id","gender","looking_for","age","language"} ko'rinishidagi lug'atlar.
    Ikkalasi uchun ham "pending" holatda taklif yaratiladi.
    """
    proposal_id = uuid.uuid4().hex[:16]
    payload = {
        "requester_id": requester["user_id"],
        "requester_gender": requester["gender"],
        "requester_looking_for": requester["looking_for"],
        "requester_age": requester["age"],
        "requester_language": requester["language"],
        "requester_city": requester.get("city"),
        "requester_search_scope": requester.get("search_scope", "country"),
        "requester_decision": "pending",
        "candidate_id": candidate["user_id"],
        "candidate_gender": candidate["gender"],
        "candidate_looking_for": candidate["looking_for"],
        "candidate_age": candidate["age"],
        "candidate_language": candidate["language"],
        "candidate_city": candidate.get("city"),
        "candidate_search_scope": candidate.get("search_scope", "country"),
        "candidate_decision": "pending",
    }
    await redis_client.set(_proposal_key(proposal_id), json.dumps(payload), ex=PROPOSAL_TTL_SECONDS)
    return proposal_id


async def get_proposal(proposal_id: str) -> dict | None:
    raw = await redis_client.get(_proposal_key(proposal_id))
    return json.loads(raw) if raw else None


async def set_decision(proposal_id: str, user_id: int, decision: str) -> dict:
    """
    `decision` "accepted" yoki "declined" bo'lishi mumkin.
    Qaytaradi: {"status": "invalid" | "declined" | "waiting_partner" | "matched", "proposal": {...}}
    """
    token = await _acquire_lock()
    try:
        proposal = await get_proposal(proposal_id)
        if not proposal:
            return {"status": "invalid", "proposal": None}

        if user_id == proposal["requester_id"]:
            role = "requester_decision"
        elif user_id == proposal["candidate_id"]:
            role = "candidate_decision"
        else:
            return {"status": "invalid", "proposal": None}

        if proposal[role] != "pending":
            return {"status": "invalid", "proposal": None}  # allaqachon javob bergan

        proposal[role] = decision

        if decision == "declined":
            await redis_client.delete(_proposal_key(proposal_id))
            return {"status": "declined", "proposal": proposal}

        if proposal["requester_decision"] == "accepted" and proposal["candidate_decision"] == "accepted":
            await redis_client.delete(_proposal_key(proposal_id))
            return {"status": "matched", "proposal": proposal}

        # hali ikkinchi tomon javob bermagan
        await redis_client.set(_proposal_key(proposal_id), json.dumps(proposal), ex=PROPOSAL_TTL_SECONDS)
        return {"status": "waiting_partner", "proposal": proposal}
    finally:
        await _release_lock(token)


async def cancel_proposals_by_user(user_id: int) -> list[dict]:
    """
    Foydalanuvchi qidiruvni bekor qilganda, u ishtirok etayotgan (hali hal
    bo'lmagan) barcha takliflarni bekor qiladi. Boshqa tomonga xabar berish
    uchun ro'yxatini qaytaradi.
    """
    cancelled = []
    async for key in redis_client.scan_iter(match="matching:proposal:*"):
        raw = await redis_client.get(key)
        if not raw:
            continue
        proposal = json.loads(raw)
        if proposal["requester_id"] == user_id or proposal["candidate_id"] == user_id:
            await redis_client.delete(key)
            cancelled.append(proposal)
    return cancelled


# ---------------------------------------------------------------------------
# Natija (frontend polling uchun)
# ---------------------------------------------------------------------------

def _result_key(user_id: int) -> str:
    return f"matching:result:{user_id}"


async def set_result(user_id: int, outcome: str, **extra):
    payload = json.dumps({"outcome": outcome, **extra})
    await redis_client.set(_result_key(user_id), payload, ex=RESULT_TTL_SECONDS)


async def pop_result(user_id: int) -> dict | None:
    key = _result_key(user_id)
    raw = await redis_client.get(key)
    if raw is None:
        return None
    await redis_client.delete(key)
    return json.loads(raw)
