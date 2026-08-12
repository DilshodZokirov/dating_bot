"""
FastAPI (`api`) jarayoni aiogram Bot obyektiga ega emas (u alohida `bot` konteynerida
ishlaydi), shuning uchun Telegram'ga xabar yuborish kerak bo'lganda to'g'ridan-to'g'ri
Telegram Bot HTTP API'siga murojaat qilamiz.
"""

import httpx

from app.config import settings
from app.i18n import t

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{settings.bot_token}"


async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
        resp.raise_for_status()
        return resp.json()


def _webapp_inline_markup(lang: str = "uz", button_key: str = "open_miniapp") -> dict | None:
    if not settings.webapp_url:
        return None
    url = f"{settings.webapp_url.rstrip('/')}/webapp/?v=saved1"
    labels = {
        "open_miniapp": {
            "uz": "📱 Mini Appni ochish",
            "ru": "📱 Открыть Mini App",
            "en": "📱 Open Mini App",
        },
        "open_to_chat": {
            "uz": "💬 Suhbatlashish",
            "ru": "💬 Общаться",
            "en": "💬 Start chat",
        },
    }
    label = labels.get(button_key, labels["open_miniapp"]).get(lang, labels["open_miniapp"]["uz"])
    return {"inline_keyboard": [[{"text": label, "web_app": {"url": url}}]]}


async def notify_match_found(
    user_id: int,
    lang: str,
    other_name: str,
    other_age: int,
    other_gender: str,
):
    """Mos suhbatdosh topilganda Telegram inline xabar."""
    gender_label = t(lang, "gender_male" if other_gender == "male" else "gender_female")
    text = t(lang, "proposal_text", name=other_name, age=other_age, gender=gender_label)
    markup = _webapp_inline_markup(lang, "open_to_chat")
    try:
        await send_message(user_id, text, markup)
    except Exception as e:
        print(f"notify_match_found {user_id}: {e}", flush=True)


async def notify_saved_invite(
    user_id: int,
    lang: str,
    other_name: str,
    other_age: int,
):
    text = {
        "uz": f"💫 <b>{other_name}</b> ({other_age}) sizni suhbatga chaqiryapti.\nMini Appni oching va javob bering.",
        "ru": f"💫 <b>{other_name}</b> ({other_age}) приглашает вас пообщаться.\nОткройте Mini App и ответьте.",
        "en": f"💫 <b>{other_name}</b> ({other_age}) invites you to chat.\nOpen the Mini App and respond.",
    }.get(lang, f"💫 {other_name} ({other_age})")
    markup = _webapp_inline_markup(lang, "open_to_chat")
    try:
        await send_message(user_id, text, markup)
    except Exception as e:
        print(f"notify_saved_invite {user_id}: {e}", flush=True)


async def notify_admins(text: str):
    for admin_id in settings.admin_id_set():
        try:
            await send_message(admin_id, text)
        except Exception as e:
            print(f"notify admin {admin_id}: {e}", flush=True)
