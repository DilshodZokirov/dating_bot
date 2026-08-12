"""
FastAPI (`api`) jarayoni aiogram Bot obyektiga ega emas (u alohida `bot` konteynerida
ishlaydi), shuning uchun Telegram'ga xabar yuborish kerak bo'lganda to'g'ridan-to'g'ri
Telegram Bot HTTP API'siga murojaat qilamiz.
"""

import httpx

from app.config import settings

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{settings.bot_token}"


async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
        resp.raise_for_status()
        return resp.json()


async def notify_admins(text: str):
    for admin_id in settings.admin_id_set():
        try:
            await send_message(admin_id, text)
        except Exception as e:
            print(f"notify admin {admin_id}: {e}", flush=True)
