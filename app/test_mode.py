"""
Dev test mode — bitta Telegram akkaunt bilan match + WebRTC ni tekshirish.

Oqim:
1. Mini Appda "Test match" → CallSession + soxta partner yaratiladi.
2. Kompyuter brauzerida /webapp/test-peer.html?token=... ochiladi.
3. Ikkalasi bir xona orqali WebRTC ulanadi.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from app.config import settings
from app.models import Gender, Language, LookingFor, SearchScope, User

# Telegram user_id bilan to'qnashmasligi uchun maxsus ID
TEST_PEER_ID = 999_000_001
TEST_PEER_NAME = "Test Partner"
TOKEN_TTL_SECONDS = 3600


def is_enabled() -> bool:
    return bool(settings.dev_test_mode)


def _secret() -> bytes:
    raw = (settings.dev_test_secret or settings.bot_token).encode()
    return hashlib.sha256(raw).digest()


def create_test_token(room_id: str, user_id: int = TEST_PEER_ID, ttl: int = TOKEN_TTL_SECONDS) -> str:
    payload = {"uid": user_id, "room": room_id, "exp": int(time.time()) + ttl}
    body = urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify_test_token(token: str, expected_room_id: str | None = None) -> dict:
    """
    Tokenni tekshiradi. Muvaffaqiyatda {"user_id", "room_id"} qaytaradi.
    Xato bo'lsa ValueError.
    """
    if not is_enabled():
        raise ValueError("test mode o'chirilgan")
    try:
        body, sig = token.split(".", 1)
    except ValueError as e:
        raise ValueError("token formati noto'g'ri") from e

    expected = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise ValueError("token imzosi noto'g'ri")

    pad = "=" * (-len(body) % 4)
    payload = json.loads(urlsafe_b64decode(body + pad))
    if int(payload.get("exp", 0)) < time.time():
        raise ValueError("token eskirgan")

    room_id = payload.get("room")
    user_id = int(payload.get("uid", 0))
    if not room_id or not user_id:
        raise ValueError("token ma'lumoti yetarli emas")
    if expected_room_id is not None and room_id != expected_room_id:
        raise ValueError("token xona bilan mos kelmaydi")

    return {"user_id": user_id, "room_id": room_id}


async def ensure_test_peer(session, language: Language = Language.uz) -> User:
    peer = await session.get(User, TEST_PEER_ID)
    if peer:
        return peer

    peer = User(
        id=TEST_PEER_ID,
        name=TEST_PEER_NAME,
        age=21,
        gender=Gender.female,
        looking_for=LookingFor.any,
        language=language,
        bio="Dev test partner (soxta foydalanuvchi)",
        city=None,
        search_scope=SearchScope.country,
        is_verified=True,
        is_banned=False,
        is_in_call=False,
    )
    session.add(peer)
    await session.commit()
    await session.refresh(peer)
    return peer
