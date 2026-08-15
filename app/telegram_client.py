"""
FastAPI (`api`) jarayoni aiogram Bot obyektiga ega emas (u alohida `bot` konteynerida
ishlaydi), shuning uchun Telegram'ga xabar yuborish kerak bo'lganda to'g'ridan-to'g'ri
Telegram Bot HTTP API'siga murojaat qilamiz.
"""

import httpx

from app.config import settings

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{settings.bot_token}"


def webapp_url() -> str | None:
    if not settings.webapp_url:
        return None
    return f"{settings.webapp_url.rstrip('/')}/webapp/?v=onesearch2"


async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
        resp.raise_for_status()
        return resp.json()


def proposal_keyboard(
    proposal_id: str,
    accept_label: str,
    decline_label: str,
    open_label: str | None = None,
) -> dict:
    rows = [
        [
            {"text": accept_label, "callback_data": f"p:a:{proposal_id}"},
            {"text": decline_label, "callback_data": f"p:d:{proposal_id}"},
        ]
    ]
    url = webapp_url()
    if url and open_label:
        rows.append([{"text": open_label, "web_app": {"url": url}}])
    return {"inline_keyboard": rows}


def phone_request_keyboard(request_id: int, accept_label: str, decline_label: str) -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": accept_label, "callback_data": f"ph:a:{request_id}"},
                {"text": decline_label, "callback_data": f"ph:d:{request_id}"},
            ]
        ]
    }


def webapp_open_keyboard(label: str) -> dict | None:
    url = webapp_url()
    if not url:
        return None
    return {"inline_keyboard": [[{"text": label, "web_app": {"url": url}}]]}


def contact_request_keyboard(label: str) -> dict:
    return {
        "keyboard": [[{"text": label, "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }


async def notify_admins(text: str):
    for admin_id in settings.admin_id_set():
        try:
            await send_message(admin_id, text)
        except Exception as e:
            print(f"notify admin {admin_id}: {e}", flush=True)
