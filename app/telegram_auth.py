"""
Telegram Mini App yuboradigan `initData`ni tekshirish.

Mini App JS orqali har bir so'rovda Telegram.WebApp.initData qiymatini yuboradi.
Bu qiymat bot tokeni bilan imzolangan bo'ladi — shu orqali so'rov haqiqatan
Telegram'dan kelayotganini va foydalanuvchi ID'sini soxtalashtirib bo'lmasligini
tasdiqlaymiz.

Rasmiy hujjat: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""

import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from app.config import settings


class InitDataError(Exception):
    pass


def validate_init_data(init_data: str, max_age_seconds: int = 86400) -> dict:
    """
    initData satrini tekshiradi va ichidagi foydalanuvchi ma'lumotini qaytaradi.
    Noto'g'ri yoki eskirgan bo'lsa InitDataError chiqaradi.
    """
    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise InitDataError("hash topilmadi")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", settings.bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise InitDataError("hash mos kelmadi — soxta so'rov bo'lishi mumkin")

    auth_date = int(parsed.get("auth_date", 0))
    import time

    if time.time() - auth_date > max_age_seconds:
        raise InitDataError("initData eskirgan")

    user_raw = parsed.get("user")
    if not user_raw:
        raise InitDataError("user ma'lumoti topilmadi")

    return json.loads(user_raw)
