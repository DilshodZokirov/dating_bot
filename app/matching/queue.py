"""
Matching queue — Redis orqali.

Oqim (ikki tomonlama rozilik / mutual double opt-in):
1. Qidiruvda mos kandidat qidiriladi (jins, til, shahar, yosh oralig'i).
2. Topilsa — ikkalasiga taklif.
3. Ikkalasi rozilik bersa — qo'ng'iroq.
4. Rad / bekor — ikkinchi tomon qayta qidiruvga.
"""

import asyncio
import json
import uuid

import redis.asyncio as redis

from app.config import settings
from app.topics import topic_compatible

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

LOCK_KEY = "matching:lock"
LOCK_TTL_MS = 5000

PROPOSAL_TTL_SECONDS = 120
RESULT_TTL_SECONDS = 600
SAVED_INVITE_TTL_SECONDS = 600


def _queue_key(looking_for: str) -> str:
    return f"matching:queue:{looking_for}"


async def _acquire_lock() -> str:
    token = str(uuid.uuid4())
    while True:
        ok = await redis_client.set(LOCK_KEY, token, nx=True, px=LOCK_TTL_MS)
        if ok:
            return token
        await asyncio.sleep(0.05)


async def _release_lock(token: str):
    current = await redis_client.get(LOCK_KEY)
    if current == token:
        await redis_client.delete(LOCK_KEY)


def _pref_ages(payload: dict) -> tuple[int, int]:
    lo = int(payload["prefer_age_min"]) if payload.get("prefer_age_min") is not None else 12
    hi = int(payload["prefer_age_max"]) if payload.get("prefer_age_max") is not None else 100
    if hi < lo:
        lo, hi = hi, lo
    return lo, hi


def _age_pref_compatible(
    age_a: int, prefer_min_a: int, prefer_max_a: int,
    age_b: int, prefer_min_b: int, prefer_max_b: int,
) -> bool:
    """Ikki tomonning yosh oralig'i bir-biriga mos kelishi kerak."""
    return prefer_min_a <= age_b <= prefer_max_a and prefer_min_b <= age_a <= prefer_max_b


def _city_compatible(a_city: str | None, a_scope: str, b_city: str | None, b_scope: str) -> bool:
    if a_scope == "city" and a_city and a_city != b_city:
        return False
    if b_scope == "city" and b_city and b_city != a_city:
        return False
    return True


def _candidate_compatible(
    gender: str,
    looking_for: str,
    age: int,
    language: str,
    city: str | None,
    search_scope: str,
    prefer_age_min: int,
    prefer_age_max: int,
    match_topic: str,
    candidate: dict,
    exclude_ids: set[int],
) -> bool:
    if candidate.get("user_id") in exclude_ids:
        return False
    c_min, c_max = _pref_ages(candidate)
    if not _age_pref_compatible(
        age, prefer_age_min, prefer_age_max,
        candidate["age"], c_min, c_max,
    ):
        return False
    if candidate.get("language") != language:
        return False
    if not _city_compatible(
        city, search_scope, candidate.get("city"), candidate.get("search_scope", "country")
    ):
        return False
    if looking_for != "any" and candidate["gender"] != looking_for:
        return False
    if candidate["looking_for"] != "any" and candidate["looking_for"] != gender:
        return False
    if not topic_compatible(match_topic, candidate.get("match_topic")):
        return False
    return True


async def count_compatible_waiters(
    gender: str,
    looking_for: str,
    age: int,
    language: str,
    city: str | None,
    search_scope: str,
    prefer_age_min: int = 12,
    prefer_age_max: int = 100,
    match_topic: str = "any",
    exclude_ids: set[int] | None = None,
) -> int:
    """
    Hozir navbatda turgan va shu sozlamalar bilan mos keladigan odamlar soni.
    UI uchun — foydalanuvchi bo‘sh qidiruvga vaqt sarflamasin.
    """
    exclude_ids = set(exclude_ids or set())
    queue_names = [_queue_key(gender), _queue_key("any")]
    seen_queues: set[str] = set()
    seen_users: set[int] = set()
    count = 0
    for q in queue_names:
        if q in seen_queues:
            continue
        seen_queues.add(q)
        raw_candidates = await redis_client.lrange(q, 0, -1)
        for raw in raw_candidates:
            try:
                candidate = json.loads(raw)
            except Exception:
                continue
            uid = candidate.get("user_id")
            if uid is None or uid in seen_users:
                continue
            if not _candidate_compatible(
                gender, looking_for, age, language, city, search_scope,
                prefer_age_min, prefer_age_max, match_topic, candidate, exclude_ids,
            ):
                continue
            seen_users.add(uid)
            count += 1
    return count


async def find_candidate(
    gender: str,
    looking_for: str,
    age: int,
    language: str,
    city: str | None,
    search_scope: str,
    prefer_age_min: int = 12,
    prefer_age_max: int = 100,
    match_topic: str = "any",
    exclude_ids: set[int] | None = None,
) -> dict | None:
    exclude_ids = exclude_ids or set()
    token = await _acquire_lock()
    try:
        queue_names = [_queue_key(gender), _queue_key("any")]
        # unique preserve order
        seen = set()
        queues = []
        for q in queue_names:
            if q not in seen:
                seen.add(q)
                queues.append(q)

        for opposite_queue in queues:
            raw_candidates = await redis_client.lrange(opposite_queue, 0, -1)
            for raw in raw_candidates:
                candidate = json.loads(raw)
                if not _candidate_compatible(
                    gender, looking_for, age, language, city, search_scope,
                    prefer_age_min, prefer_age_max, match_topic, candidate, exclude_ids,
                ):
                    continue
                # Allaqachon boshqa taklifda band bo‘lsa — o‘tkazib yuboramiz
                try:
                    cuid = int(candidate["user_id"])
                except Exception:
                    continue
                if await redis_client.get(_user_proposal_key(cuid)):
                    await redis_client.lrem(opposite_queue, 1, raw)
                    continue
                await redis_client.lrem(opposite_queue, 1, raw)
                return candidate
        return None
    finally:
        await _release_lock(token)


async def join_queue(
    user_id: int,
    gender: str,
    looking_for: str,
    age: int,
    language: str,
    city: str | None,
    search_scope: str,
    prefer_age_min: int = 12,
    prefer_age_max: int = 100,
    match_topic: str = "any",
):
    await cancel_wait(user_id, looking_for)
    for lf in ("male", "female", "any"):
        if lf != looking_for:
            await cancel_wait(user_id, lf)

    my_queue = _queue_key(looking_for)
    payload = json.dumps({
        "user_id": user_id,
        "gender": gender,
        "looking_for": looking_for,
        "age": age,
        "language": language,
        "city": city,
        "search_scope": search_scope,
        "prefer_age_min": prefer_age_min,
        "prefer_age_max": prefer_age_max,
        "match_topic": match_topic or "any",
    })
    await redis_client.rpush(my_queue, payload)


async def cancel_wait(user_id: int, looking_for: str):
    my_queue = _queue_key(looking_for)
    raw_candidates = await redis_client.lrange(my_queue, 0, -1)
    for raw in raw_candidates:
        candidate = json.loads(raw)
        if candidate["user_id"] == user_id:
            await redis_client.lrem(my_queue, 0, raw)


async def requeue_user(payload: dict):
    await join_queue(
        payload["user_id"],
        payload["gender"],
        payload["looking_for"],
        payload["age"],
        payload["language"],
        payload.get("city"),
        payload.get("search_scope", "country"),
        int(payload["prefer_age_min"]) if payload.get("prefer_age_min") is not None else 12,
        int(payload["prefer_age_max"]) if payload.get("prefer_age_max") is not None else 100,
        payload.get("match_topic") or "any",
    )


def _proposal_key(proposal_id: str) -> str:
    return f"matching:proposal:{proposal_id}"


def _user_proposal_key(user_id: int) -> str:
    """Foydalanuvchi hozirgi taklifda band — yangi juft chiqmasin."""
    return f"matching:user_proposal:{user_id}"


async def get_user_proposal_id(user_id: int) -> str | None:
    return await redis_client.get(_user_proposal_key(user_id))


async def user_is_reserved(user_id: int) -> bool:
    return bool(await get_user_proposal_id(user_id))


async def _bind_user_proposal(user_id: int, proposal_id: str, ttl: int) -> None:
    await redis_client.set(_user_proposal_key(user_id), proposal_id, ex=ttl)


async def _clear_user_proposal(user_id: int, proposal_id: str | None = None) -> None:
    key = _user_proposal_key(user_id)
    if proposal_id is None:
        await redis_client.delete(key)
        return
    cur = await redis_client.get(key)
    if cur == proposal_id:
        await redis_client.delete(key)


async def _clear_proposal_reservations(proposal: dict, proposal_id: str | None = None) -> None:
    pid = proposal_id
    for uid in (proposal.get("requester_id"), proposal.get("candidate_id")):
        if uid is not None:
            await _clear_user_proposal(int(uid), pid)


def _side_fields(prefix: str, data: dict) -> dict:
    return {
        f"{prefix}_id": data["user_id"],
        f"{prefix}_gender": data["gender"],
        f"{prefix}_looking_for": data["looking_for"],
        f"{prefix}_age": data["age"],
        f"{prefix}_language": data["language"],
        f"{prefix}_city": data.get("city"),
        f"{prefix}_search_scope": data.get("search_scope", "country"),
        f"{prefix}_prefer_age_min": int(data["prefer_age_min"]) if data.get("prefer_age_min") is not None else 12,
        f"{prefix}_prefer_age_max": int(data["prefer_age_max"]) if data.get("prefer_age_max") is not None else 100,
        f"{prefix}_match_topic": data.get("match_topic") or "any",
        f"{prefix}_decision": "pending",
    }


async def create_mutual_proposal(requester: dict, candidate: dict, ttl: int | None = None) -> str | None:
    """
    Ikkalasini ham band qiladi. Agar birortasi allaqachon taklifda bo‘lsa — None.
    """
    ttl_sec = ttl or PROPOSAL_TTL_SECONDS
    token = await _acquire_lock()
    try:
        req_id = int(requester["user_id"])
        cand_id = int(candidate["user_id"])
        if await user_is_reserved(req_id) or await user_is_reserved(cand_id):
            return None

        proposal_id = uuid.uuid4().hex[:16]
        payload = {}
        payload.update(_side_fields("requester", requester))
        payload.update(_side_fields("candidate", candidate))
        await redis_client.set(
            _proposal_key(proposal_id),
            json.dumps(payload),
            ex=ttl_sec,
        )
        await _bind_user_proposal(req_id, proposal_id, ttl_sec)
        await _bind_user_proposal(cand_id, proposal_id, ttl_sec)
        return proposal_id
    finally:
        await _release_lock(token)


async def get_proposal(proposal_id: str) -> dict | None:
    raw = await redis_client.get(_proposal_key(proposal_id))
    return json.loads(raw) if raw else None


async def set_decision(proposal_id: str, user_id: int, decision: str) -> dict:
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
            return {"status": "invalid", "proposal": None}

        proposal[role] = decision

        if decision == "declined":
            await redis_client.delete(_proposal_key(proposal_id))
            await _clear_proposal_reservations(proposal, proposal_id)
            return {"status": "declined", "proposal": proposal}

        if proposal["requester_decision"] == "accepted" and proposal["candidate_decision"] == "accepted":
            await redis_client.delete(_proposal_key(proposal_id))
            await _clear_proposal_reservations(proposal, proposal_id)
            return {"status": "matched", "proposal": proposal}

        # Bitta tomon qabul qildi — ikkalasi ham band bo‘lib qoladi
        await redis_client.set(_proposal_key(proposal_id), json.dumps(proposal), ex=PROPOSAL_TTL_SECONDS)
        await _bind_user_proposal(int(proposal["requester_id"]), proposal_id, PROPOSAL_TTL_SECONDS)
        await _bind_user_proposal(int(proposal["candidate_id"]), proposal_id, PROPOSAL_TTL_SECONDS)
        return {"status": "waiting_partner", "proposal": proposal}
    finally:
        await _release_lock(token)


async def cancel_proposals_by_user(user_id: int) -> list[dict]:
    cancelled = []
    async for key in redis_client.scan_iter(match="matching:proposal:*"):
        raw = await redis_client.get(key)
        if not raw:
            continue
        proposal = json.loads(raw)
        if proposal["requester_id"] == user_id or proposal["candidate_id"] == user_id:
            pid = key.split(":")[-1]
            await redis_client.delete(key)
            await _clear_proposal_reservations(proposal, pid)
            cancelled.append(proposal)
    # Orphan band kalit
    await _clear_user_proposal(user_id)
    return cancelled


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
