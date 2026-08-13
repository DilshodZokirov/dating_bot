"""
FastAPI (`api`) jarayoni aiogram Bot obyektiga ega emas (u alohida `bot` konteynerida
ishlaydi), shuning uchun Telegram'ga xabar yuborish kerak bo'lganda to'g'ridan-to'g'ri
Telegram Bot HTTP API'siga murojaat qilamiz.
"""

import httpx

from app.config import settings
from app.i18n import t

TELEGRAM_API_BASE = f"https://api.telegram.org/bot{settings.bot_token}"


def _webapp_url() -> str | None:
    if not settings.webapp_url:
        return None
    return f"{settings.webapp_url.rstrip('/')}/webapp/?v=i18n4"


async def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{TELEGRAM_API_BASE}/sendMessage", json=payload)
        resp.raise_for_status()
        return resp.json()


async def set_chat_menu_button(chat_id: int, text: str, url: str):
    """Foydalanuvchi uchun Menu tugmasi matnini yangilash."""
    payload = {
        "chat_id": chat_id,
        "menu_button": {
            "type": "web_app",
            "text": text[:64],
            "web_app": {"url": url},
        },
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{TELEGRAM_API_BASE}/setChatMenuButton", json=payload)
        resp.raise_for_status()
        return resp.json()


def reply_webapp_keyboard(lang: str) -> dict | None:
    url = _webapp_url()
    if not url:
        return None
    return {
        "keyboard": [[{"text": t(lang, "kb_search_call"), "web_app": {"url": url}}]],
        "resize_keyboard": True,
    }


async def sync_user_language_ui(chat_id: int, lang: str):
    """
    Mini Appda til o'zgarganda bot tomonini ham yangilaydi:
    - xabar yangi tilda
    - reply keyboard
    - chat Menu tugmasi
    """
    url = _webapp_url()
    kb = reply_webapp_keyboard(lang)
    try:
        await send_message(chat_id, t(lang, "lang_changed"), reply_markup=kb)
    except Exception as e:
        print(f"sync lang message {chat_id}: {e}", flush=True)
    if url:
        try:
            await set_chat_menu_button(chat_id, t(lang, "menu_btn"), url)
        except Exception as e:
            print(f"sync lang menu {chat_id}: {e}", flush=True)


async def notify_admins(text: str):
    for admin_id in settings.admin_id_set():
        try:
            await send_message(admin_id, text)
        except Exception as e:
            print(f"notify admin {admin_id}: {e}", flush=True)
