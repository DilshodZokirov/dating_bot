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


def _proposal_callback_markup(lang: str, proposal_id: str) -> dict:
    """Telegram bot inline: Roziman / Yo'q (callback, webapp emas)."""
    return {
        "inline_keyboard": [
            [
                {"text": t(lang, "btn_accept"), "callback_data": f"p:a:{proposal_id}"},
                {"text": t(lang, "btn_decline"), "callback_data": f"p:d:{proposal_id}"},
            ]
        ]
    }


def _webapp_open_markup(lang: str) -> dict | None:
    """Faqat qo'ng'iroq boshlanganda Mini App ochish."""
    if not settings.webapp_url:
        return None
    url = f"{settings.webapp_url.rstrip('/')}/webapp/?v=tg1"
    label = {"uz": "📞 Qo'ng'iroqni ochish", "ru": "📞 Открыть звонок", "en": "📞 Open call"}.get(
        lang, "📞 Qo'ng'iroqni ochish"
    )
    return {"inline_keyboard": [[{"text": label, "web_app": {"url": url}}]]}


async def notify_match_found(
    user_id: int,
    lang: str,
    other_name: str,
    other_age: int,
    other_gender: str,
    proposal_id: str,
):
    """Mos suhbatdosh — Telegram botda inline Roziman/Yo'q."""
    gender_label = t(lang, "gender_male" if other_gender == "male" else "gender_female")
    text = t(lang, "proposal_text", name=other_name, age=other_age, gender=gender_label)
    markup = _proposal_callback_markup(lang, proposal_id)
    try:
        await send_message(user_id, text, markup)
    except Exception as e:
        print(f"notify_match_found {user_id}: {e}", flush=True)


async def notify_saved_invite(
    user_id: int,
    lang: str,
    other_name: str,
    other_age: int,
    proposal_id: str,
):
    text = {
        "uz": f"💫 <b>{other_name}</b> ({other_age}) sizni suhbatga chaqiryapti.\nQabul qilasizmi?",
        "ru": f"💫 <b>{other_name}</b> ({other_age}) приглашает вас пообщаться.\nПринять?",
        "en": f"💫 <b>{other_name}</b> ({other_age}) invites you to chat.\nAccept?",
    }.get(lang, f"💫 {other_name} ({other_age})")
    markup = _proposal_callback_markup(lang, proposal_id)
    try:
        await send_message(user_id, text, markup)
    except Exception as e:
        print(f"notify_saved_invite {user_id}: {e}", flush=True)


async def notify_call_ready(user_id: int, lang: str, room_id: str = ""):
    text = t(lang, "match_started", room_id=room_id or "—")
    markup = _webapp_open_markup(lang)
    try:
        await send_message(user_id, text, markup)
    except Exception as e:
        print(f"notify_call_ready {user_id}: {e}", flush=True)


async def notify_text(user_id: int, lang: str, key: str, **kwargs):
    try:
        await send_message(user_id, t(lang, key, **kwargs))
    except Exception as e:
        print(f"notify_text {user_id}: {e}", flush=True)


async def notify_admins(text: str):
    for admin_id in settings.admin_id_set():
        try:
            await send_message(admin_id, text)
        except Exception as e:
            print(f"notify admin {admin_id}: {e}", flush=True)
