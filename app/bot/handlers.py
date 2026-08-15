from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    WebAppInfo,
    MenuButtonWebApp,
)

from app.bot.states import Registration
from app.config import settings
from app.database import async_session
from app.i18n import t
from app.link_title import (
    ensure_localized_result,
    extract_movie_from_ocr_text,
    extract_urls_from_message,
    identify_movie_from_image_bytes,
    identify_movie_from_video_bytes,
    resolve_movie_title_from_message,
)
from app.matching.age_brackets import default_prefer_ages
from app.matching.queue import cancel_proposals_by_user, cancel_wait, requeue_user, set_result
from app.matching.respond import respond_to_proposal
from app.phone_share import accept_phone_share, complete_phone_await_after_contact, decline_phone_share
from app.models import Gender, Language, LookingFor, ReportStatus, User
from app.moderation import list_open_reports, mark_report, set_user_banned
from app.telegram_client import webapp_open_keyboard

router = Router()


def _webapp_url() -> str | None:
    if not settings.webapp_url:
        return None
    return f"{settings.webapp_url.rstrip('/')}/webapp/?v=onesearch2"


def _ui_lang(user: User | None) -> str:
    """Bot/UI matnlari — dastur tili (ui_language), yo‘q bo‘lsa matching tili."""
    if not user:
        return "uz"
    ui = getattr(user, "ui_language", None)
    if ui is not None:
        return ui.value if hasattr(ui, "value") else str(ui)
    return user.language.value


def _movie_progress_cb(wait: Message, lang: str):
    """Status xabarini bosqichma-bosqich yangilash + typing."""
    last = {"step": ""}

    async def on_progress(step: str) -> None:
        if not step or step == last["step"]:
            return
        last["step"] = step
        key = f"link_progress_{step}"
        text = t(lang, key)
        if text == key:
            text = t(lang, "link_looking")
        try:
            await wait.bot.send_chat_action(wait.chat.id, ChatAction.TYPING)
        except Exception:
            pass
        try:
            await wait.edit_text(text)
        except Exception:
            pass

    return on_progress


async def _finish_progress(wait: Message | None) -> None:
    if not wait:
        return
    try:
        await wait.delete()
    except Exception:
        pass


# Bir foydalanuvchi / media group — ikki marta parallel qidiruvni to‘xtatish
_movie_busy_users: set[int] = set()
_movie_seen_groups: dict[str, float] = {}


def _movie_lookup_busy(message: Message) -> bool:
    """True bo‘lsa — bu so‘rovni o‘tkazib yuborish (dublikat)."""
    import time

    uid = message.from_user.id if message.from_user else 0
    gid = getattr(message, "media_group_id", None)
    now = time.time()
    # Eski group kalitlarini tozalash
    stale = [k for k, ts in _movie_seen_groups.items() if now - ts > 60]
    for k in stale:
        _movie_seen_groups.pop(k, None)
    if gid:
        if gid in _movie_seen_groups:
            return True
        _movie_seen_groups[gid] = now
    if uid in _movie_busy_users:
        return True
    _movie_busy_users.add(uid)
    return False


def _movie_lookup_done(message: Message) -> None:
    uid = message.from_user.id if message.from_user else 0
    _movie_busy_users.discard(uid)


async def _set_user_menu(message: Message, lang: str) -> None:
    """Bitta kirish nuqtasi: Telegram Menu → Mini App."""
    url = _webapp_url()
    if not url:
        return
    try:
        await message.bot.set_chat_menu_button(
            chat_id=message.chat.id,
            menu_button=MenuButtonWebApp(
                text=t(lang, "menu_btn")[:64],
                web_app=WebAppInfo(url=url),
            ),
        )
    except Exception as e:
        print(f"set_chat_menu_button {message.chat.id}: {e}", flush=True)


def _clear_reply_kb() -> ReplyKeyboardRemove:
    """Eski 'Qidirish / Qo'ng'iroq' klaviaturasini olib tashlash."""
    return ReplyKeyboardRemove()

gender_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]],
    resize_keyboard=True,
)

language_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="O'zbek"), KeyboardButton(text="Русский"), KeyboardButton(text="English")],
        [KeyboardButton(text="Deutsch"), KeyboardButton(text="Tojik"), KeyboardButton(text="Turk")],
        [KeyboardButton(text="Koreys"), KeyboardButton(text="Yapon"), KeyboardButton(text="Xitoy")],
        [KeyboardButton(text="Arab")],
    ],
    resize_keyboard=True,
)

GENDER_MAP = {"Erkak": Gender.male, "Ayol": Gender.female}
OPPOSITE_GENDER = {Gender.male: LookingFor.female, Gender.female: LookingFor.male}
LANGUAGE_MAP = {
    "O'zbek": Language.uz,
    "Русский": Language.ru,
    "English": Language.en,
    "Deutsch": Language.de,
    "Tojik": Language.tg,
    "Turk": Language.tr,
    "Koreys": Language.ko,
    "Yapon": Language.ja,
    "Xitoy": Language.zh,
    "Arab": Language.ar,
}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    try:
        async with async_session() as session:
            user = await session.get(User, message.from_user.id)

        if user:
            lang = _ui_lang(user)
            await _set_user_menu(message, lang)
            if not settings.webapp_url:
                await message.answer(t(lang, "webapp_url_missing"))
            else:
                await message.answer(
                    t(lang, "welcome_back", name=user.name),
                    reply_markup=_clear_reply_kb(),
                )
            return

        await message.answer(t("uz", "reg_hello"))
        await state.set_state(Registration.name)
    except Exception as e:
        print(f"cmd_start ERROR: {e}", flush=True)
        await message.answer(f"Xato: {e}\nQayta /start yuboring.")


@router.message(Command("app"))
async def cmd_app(message: Message, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    lang = _ui_lang(user)
    if not settings.webapp_url:
        await message.answer(t(lang, "webapp_url_missing"))
        return
    await _set_user_menu(message, lang)
    await message.answer(t(lang, "search_check_app"), reply_markup=_clear_reply_kb())


@router.callback_query(F.data.startswith("p:"))
async def on_proposal_callback(callback: CallbackQuery):
    """Telegram inline: p:a:{id} qabul, p:d:{id} rad."""
    data = callback.data or ""
    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "p" or parts[1] not in ("a", "d"):
        await callback.answer("Noto'g'ri tugma", show_alert=True)
        return

    decision = "accepted" if parts[1] == "a" else "declined"
    proposal_id = parts[2]
    user_id = callback.from_user.id

    async with async_session() as session:
        user = await session.get(User, user_id)
    lang = _ui_lang(user)

    result = await respond_to_proposal(user_id, proposal_id, decision)
    outcome = result.get("outcome")

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if outcome == "invalid":
        await callback.answer(t(lang, "proposal_invalid"), show_alert=True)
        return

    if outcome == "waiting_partner":
        await callback.answer()
        await callback.message.answer(t(lang, "accepted_waiting_partner"))
        return

    if outcome == "declined":
        await callback.answer()
        await callback.message.answer(t(lang, "declined_self"))
        return

    if outcome == "livekit_missing":
        await callback.answer("LiveKit sozlanmagan", show_alert=True)
        return

    if outcome == "matched":
        await callback.answer()
        kb = webapp_open_keyboard(t(lang, "menu_btn"))
        await callback.message.answer(t(lang, "match_started"), reply_markup=kb)
        return

    await callback.answer()


@router.callback_query(F.data.startswith("ph:"))
async def on_phone_share_callback(callback: CallbackQuery):
    """Telefon so‘rovi: ph:a:{id} / ph:d:{id}."""
    data = callback.data or ""
    parts = data.split(":", 2)
    if len(parts) != 3 or parts[0] != "ph" or parts[1] not in ("a", "d") or not parts[2].isdigit():
        await callback.answer("Noto'g'ri tugma", show_alert=True)
        return

    user_id = callback.from_user.id
    request_id = int(parts[2])
    async with async_session() as session:
        user = await session.get(User, user_id)
    lang = _ui_lang(user)

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    if parts[1] == "d":
        result = await decline_phone_share(request_id, user_id)
        await callback.answer()
        if result.get("status") == "declined":
            await callback.message.answer(t(lang, "declined_self"))
        else:
            await callback.message.answer(t(lang, "proposal_invalid"))
        return

    result = await accept_phone_share(request_id, user_id)
    await callback.answer()
    if result.get("status") == "shared":
        await callback.message.answer(t(lang, "phone_saved_thanks"))
    elif result.get("status") == "need_contact":
        pass  # contact keyboard allaqachon yuborilgan
    else:
        await callback.message.answer(t(lang, "proposal_invalid"))


@router.message(F.contact)
async def on_contact_shared(message: Message):
    """Telegram contact — telefon saqlash + kutayotgan so‘rovni yakunlash."""
    contact = message.contact
    if not contact or not message.from_user:
        return
    # Faqat o‘z kontaktini qabul qilamiz
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer("Iltimos, o‘zingizning telefon raqamingizni yuboring.")
        return
    phone = contact.phone_number or ""
    if phone and not phone.startswith("+"):
        phone = f"+{phone}"
    user_id = message.from_user.id
    async with async_session() as session:
        user = await session.get(User, user_id)
    lang = _ui_lang(user)

    delivered = await complete_phone_await_after_contact(user_id, phone)
    await message.answer(
        t(lang, "phone_saved_thanks"),
        reply_markup=ReplyKeyboardRemove(),
    )
    if delivered:
        await message.answer(t(lang, "accepted_confirmed"))


@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip()[:64])
    await message.answer("Yoshingizni kiriting (faqat raqam):")
    await state.set_state(Registration.age)


@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, yoshingizni raqam bilan kiriting.")
        return

    age = int(message.text)
    if age < settings.min_age:
        await message.answer(f"Kechirasiz, bu botdan faqat {settings.min_age}+ yoshdagi foydalanuvchilar foydalana oladi.")
        await state.clear()
        return
    if age > 100:
        await message.answer("Yoshni to'g'ri kiriting.")
        return

    await state.update_data(age=age)
    await message.answer("Jinsingizni tanlang:", reply_markup=gender_kb)
    await state.set_state(Registration.gender)


@router.message(Registration.gender, F.text.in_(GENDER_MAP.keys()))
async def process_gender(message: Message, state: FSMContext):
    gender = GENDER_MAP[message.text]
    await state.update_data(gender=gender, looking_for=OPPOSITE_GENDER[gender])
    await message.answer(
        "Qaysi tilda suhbatlashmoqchisiz?\n"
        "(Qidiruv shu til bo‘yicha mos suhbatdosh topadi)",
        reply_markup=language_kb,
    )
    await state.set_state(Registration.language)


@router.message(Registration.language, F.text.in_(LANGUAGE_MAP.keys()))
async def process_language(message: Message, state: FSMContext):
    data = await state.update_data(language=LANGUAGE_MAP[message.text])

    async with async_session() as session:
        pref_min, pref_max = default_prefer_ages(data["age"])
        user = User(
            id=message.from_user.id,
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            looking_for=data["looking_for"],
            language=data["language"],
            ui_language=data["language"],
            prefer_age_min=pref_min,
            prefer_age_max=pref_max,
            is_verified=False,  # keyinchalik yosh tasdiqlash bosqichi qo'shiladi
        )
        session.add(user)
        await session.commit()

    await state.clear()
    lang = data["language"].value if hasattr(data["language"], "value") else data["language"]
    await _set_user_menu(message, lang)
    await message.answer(
        t(lang, "reg_done", name=data["name"]),
        reply_markup=_clear_reply_kb(),
    )
    await message.answer(t(lang, "how_it_works"))


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    lang = _ui_lang(user)
    if user:
        await _set_user_menu(message, lang)
    await message.answer(
        t(lang, "how_it_works"),
        reply_markup=_clear_reply_kb() if user else None,
    )
    await message.answer(t(lang, "help_commands"))
    await message.answer(t(lang, "link_guide"))


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """Eski buyruq — faqat Menu'ga yo‘naltiradi (reklama qilinmaydi)."""
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

    if not user:
        await message.answer(t("uz", "need_register"))
        return

    lang = _ui_lang(user)
    await _set_user_menu(message, lang)
    await message.answer(
        t(lang, "search_check_app"),
        reply_markup=_clear_reply_kb(),
    )


@router.message(Command("stop"))
async def cmd_stop(message: Message, state: FSMContext):
    """Faol qidiruvni va javob kutayotgan takliflarni bekor qiladi."""
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

    if user:
        await cancel_wait(user.id, user.looking_for.value)
        for lf in ("male", "female", "any"):
            if lf != user.looking_for.value:
                await cancel_wait(user.id, lf)
        cancelled = await cancel_proposals_by_user(user.id)
        for proposal in cancelled:
            if proposal["requester_id"] == user.id:
                other = {
                    "user_id": proposal["candidate_id"],
                    "gender": proposal["candidate_gender"],
                    "looking_for": proposal["candidate_looking_for"],
                    "age": proposal["candidate_age"],
                    "language": proposal["candidate_language"],
                    "city": proposal.get("candidate_city"),
                    "search_scope": proposal.get("candidate_search_scope", "country"),
                    "prefer_age_min": proposal.get("candidate_prefer_age_min", 12),
                    "prefer_age_max": proposal.get("candidate_prefer_age_max", 100),
                    "match_topic": proposal.get("candidate_match_topic", "any"),
                }
            else:
                other = {
                    "user_id": proposal["requester_id"],
                    "gender": proposal["requester_gender"],
                    "looking_for": proposal["requester_looking_for"],
                    "age": proposal["requester_age"],
                    "language": proposal["requester_language"],
                    "city": proposal.get("requester_city"),
                    "search_scope": proposal.get("requester_search_scope", "country"),
                    "prefer_age_min": proposal.get("requester_prefer_age_min", 12),
                    "prefer_age_max": proposal.get("requester_prefer_age_max", 100),
                    "match_topic": proposal.get("requester_match_topic", "any"),
                }
            await requeue_user(other)
            await set_result(other["user_id"], "requeued")

    await state.clear()
    lang = _ui_lang(user)
    await message.answer(t(lang, "stop_confirm"))


@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if user:
            lang = _ui_lang(user)
            await cancel_wait(user.id, user.looking_for.value)
            await session.delete(user)
            await session.commit()

    await state.clear()
    await message.answer(t(lang, "reset_confirm"), reply_markup=ReplyKeyboardRemove())


def _is_admin(user_id: int | None) -> bool:
    return bool(user_id) and user_id in settings.admin_id_set()


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ruxsat yo'q.")
        return
    await message.answer(
        "🛡 <b>Admin</b>\n\n"
        "/reports — ochiq shikoyatlar\n"
        "/ban &lt;user_id&gt; — ban\n"
        "/unban &lt;user_id&gt; — bandan chiqarish\n"
        "/report_done &lt;id&gt; — shikoyatni yopish\n"
        "/report_dismiss &lt;id&gt; — rad etish",
        parse_mode="HTML",
    )


@router.message(Command("reports"))
async def cmd_reports(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ruxsat yo'q.")
        return
    reports = await list_open_reports(limit=15)
    if not reports:
        await message.answer("Ochiq shikoyat yo'q.")
        return
    lines = ["📋 <b>Ochiq shikoyatlar</b>\n"]
    for r in reports:
        lines.append(
            f"#{r.id} · {r.reason.value}\n"
            f"  kim: <code>{r.reporter_id}</code> → <code>{r.reported_id}</code>\n"
            f"  xona: {r.room_id or '—'}\n"
            f"  /ban {r.reported_id} · /report_done {r.id}"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ruxsat yo'q.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /ban &lt;user_id&gt;", parse_mode="HTML")
        return
    uid = int(parts[1])
    user = await set_user_banned(uid, True)
    if not user:
        await message.answer(f"User {uid} topilmadi.")
        return
    await message.answer(f"🚫 Ban: <code>{uid}</code> ({user.name})", parse_mode="HTML")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ruxsat yo'q.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /unban &lt;user_id&gt;", parse_mode="HTML")
        return
    uid = int(parts[1])
    user = await set_user_banned(uid, False)
    if not user:
        await message.answer(f"User {uid} topilmadi.")
        return
    await message.answer(f"✅ Unban: <code>{uid}</code> ({user.name})", parse_mode="HTML")


@router.message(Command("report_done"))
async def cmd_report_done(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ruxsat yo'q.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /report_done &lt;id&gt;", parse_mode="HTML")
        return
    report = await mark_report(int(parts[1]), ReportStatus.reviewed)
    if not report:
        await message.answer("Shikoyat topilmadi.")
        return
    await message.answer(f"✅ Shikoyat #{report.id} yopildi.")


@router.message(Command("report_dismiss"))
async def cmd_report_dismiss(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ruxsat yo'q.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: /report_dismiss &lt;id&gt;", parse_mode="HTML")
        return
    report = await mark_report(int(parts[1]), ReportStatus.dismissed)
    if not report:
        await message.answer("Shikoyat topilmadi.")
        return
    await message.answer(f"🗑 Shikoyat #{report.id} rad etildi.")


@router.message(F.photo)
async def identify_movie_photo(message: Message, state: FSMContext):
    """Instagram ochilmasa — foydalanuvchi ekran rasmini yuboradi."""
    current = await state.get_state()
    if current:
        return
    if _movie_lookup_busy(message):
        return
    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    if user:
        lang = _ui_lang(user)

    wait = await message.answer(t(lang, "link_looking"))
    progress = _movie_progress_cb(wait, lang)

    # Caption matnida nom bo‘lsa — tilga moslab + mazmun
    if message.caption:
        from_cap = extract_movie_from_ocr_text(message.caption)
        if from_cap:
            await progress("localize")
            result = await ensure_localized_result(
                {"ok": True, "title": from_cap, "summary": "", "source": "caption"},
                lang,
                on_progress=progress,
            )
            await _finish_progress(wait)
            try:
                await _reply_movie_result(message, lang, result)
            finally:
                _movie_lookup_done(message)
            return

    try:
        await progress("download")
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        buf = await message.bot.download_file(file.file_path)
        raw = buf.read() if hasattr(buf, "read") else bytes(buf)
        print(f"photo identify: size={len(raw)} file={file.file_path}", flush=True)
        result = await identify_movie_from_image_bytes(
            raw, "image/jpeg", lang=lang, on_progress=progress
        )
        print(f"photo identify result: {result}", flush=True)
    except Exception as e:
        print(f"photo identify error: {e}", flush=True)
        result = {"ok": False, "error": "not_identified"}
    await _finish_progress(wait)
    try:
        await _reply_movie_result(message, lang, result)
    finally:
        _movie_lookup_done(message)


@router.message(F.video)
async def identify_movie_video(message: Message, state: FSMContext):
    """Foydalanuvchi videoni o‘zi yuborsa — kadr olib nomini aniqlaymiz (fayl saqlanmaydi)."""
    current = await state.get_state()
    if current:
        return
    video = message.video
    if not video:
        return
    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    if user:
        lang = _ui_lang(user)

    # Telegram Bot API getFile ~20MB
    if (video.file_size or 0) > 20 * 1024 * 1024:
        await message.answer(t(lang, "link_video_too_large"))
        return
    if _movie_lookup_busy(message):
        return

    wait = await message.answer(t(lang, "link_looking"))
    progress = _movie_progress_cb(wait, lang)
    try:
        await progress("download")
        file = await message.bot.get_file(video.file_id)
        buf = await message.bot.download_file(file.file_path)
        raw = buf.read() if hasattr(buf, "read") else bytes(buf)
        result = await identify_movie_from_video_bytes(
            raw, lang=lang, on_progress=progress
        )
    except Exception as e:
        print(f"video identify error: {e}", flush=True)
        result = {"ok": False, "error": "not_identified"}
    await _finish_progress(wait)
    try:
        await _reply_movie_result(message, lang, result)
    finally:
        _movie_lookup_done(message)


@router.message(F.document)
async def identify_movie_document(message: Message, state: FSMContext):
    """Video/rasm document sifatida yuborilsa."""
    current = await state.get_state()
    if current:
        return
    # Photo/video handler allaqachon ishlagan bo‘lsa — takrorlama
    if message.photo or message.video:
        return
    doc = message.document
    if not doc:
        return
    mime = (doc.mime_type or "").lower()
    name = (doc.file_name or "").lower()
    is_video = mime.startswith("video/") or name.endswith(
        (".mp4", ".mov", ".mkv", ".webm", ".avi")
    )
    is_image = mime.startswith("image/") or name.endswith(
        (".jpg", ".jpeg", ".png", ".webp")
    )
    if not is_video and not is_image:
        return
    if _movie_lookup_busy(message):
        return

    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    if user:
        lang = _ui_lang(user)

    if (doc.file_size or 0) > 20 * 1024 * 1024:
        await message.answer(t(lang, "link_video_too_large"))
        _movie_lookup_done(message)
        return

    wait = await message.answer(t(lang, "link_looking"))
    progress = _movie_progress_cb(wait, lang)
    try:
        await progress("download")
        file = await message.bot.get_file(doc.file_id)
        buf = await message.bot.download_file(file.file_path)
        raw = buf.read() if hasattr(buf, "read") else bytes(buf)
        if is_video:
            result = await identify_movie_from_video_bytes(
                raw, lang=lang, on_progress=progress
            )
        else:
            result = await identify_movie_from_image_bytes(
                raw, mime or "image/jpeg", lang=lang, on_progress=progress
            )
    except Exception as e:
        print(f"document identify error: {e}", flush=True)
        result = {"ok": False, "error": "not_identified"}
    await _finish_progress(wait)
    try:
        await _reply_movie_result(message, lang, result)
    finally:
        _movie_lookup_done(message)


@router.message(F.text)
async def fallback_text(message: Message, state: FSMContext):
    """Hech qaysi handler mos kelmasa — yo'l ko'rsatamiz yoki silka nomini qidiramiz."""
    current = await state.get_state()
    print(f"fallback: text={message.text!r} state={current}", flush=True)
    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    if user:
        lang = _ui_lang(user)
    if current:
        await message.answer(t(lang, "bad_step"))
        return

    # Silka bo‘lsa — sahifa/film nomini aniqlash (fayl emas)
    if extract_urls_from_message(message):
        if _movie_lookup_busy(message):
            return
        wait = await message.answer(t(lang, "link_looking"))
        progress = _movie_progress_cb(wait, lang)
        try:
            result = await resolve_movie_title_from_message(
                message, lang=lang, on_progress=progress
            )
            await _finish_progress(wait)
            await _reply_movie_result(message, lang, result)
        finally:
            _movie_lookup_done(message)
        return

    await _set_user_menu(message, lang)
    await message.answer(t(lang, "help_commands"), reply_markup=_clear_reply_kb())


async def _reply_movie_result(message: Message, lang: str, result: dict) -> None:
    if result.get("ok") and result.get("uncertain") and result.get("candidates"):
        from app.link_title import format_candidates_list

        text = t(
            lang,
            "link_found_uncertain",
            list=format_candidates_list(result["candidates"]),
        )
        await message.answer(text)
        return
    if result.get("ok") and result.get("title"):
        import html as html_lib

        title = html_lib.escape(str(result["title"]))
        summary = html_lib.escape(str(result.get("summary") or "").strip())
        text = t(lang, "link_found", title=title, summary=summary).rstrip()
        await message.answer(text)
        return
    err = result.get("error") or ""
    if err == "need_gemini":
        await message.answer(t(lang, "link_need_gemini"))
    elif err in ("no_image", "no_url", "no_frame"):
        await message.answer(t(lang, "link_need_preview"))
    elif err == "video_too_large":
        await message.answer(t(lang, "link_video_too_large"))
    else:
        await message.answer(t(lang, "link_not_found"))
