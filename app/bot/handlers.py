from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.bot.states import Registration
from app.config import settings
from app.database import async_session
from app.i18n import t
from app.matching.age_brackets import default_prefer_ages
from app.matching.queue import cancel_proposals_by_user, cancel_wait, requeue_user, set_result
from app.matching.respond import respond_to_proposal
from app.models import Gender, Language, LookingFor, ReportStatus, User
from app.moderation import list_open_reports, mark_report, set_user_banned

router = Router()


def _webapp_url() -> str | None:
    if not settings.webapp_url:
        return None
    return f"{settings.webapp_url.rstrip('/')}/webapp/?v=roulette2"


def _webapp_kb(lang: str = "uz") -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    """Mini App ochish tugmasi — video qo'ng'iroq shu yerda."""
    url = _webapp_url()
    if not url:
        print("WARNING: WEBAPP_URL bo'sh — Mini App tugmasi yuborilmaydi", flush=True)
        return ReplyKeyboardRemove()
    label = t(lang, "kb_search_call")
    print(f"Mini App URL: {url}", flush=True)
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label, web_app=WebAppInfo(url=url))]],
        resize_keyboard=True,
    )


def _webapp_inline(lang: str = "uz") -> InlineKeyboardMarkup | None:
    url = _webapp_url()
    if not url:
        return None
    label = t(lang, "kb_open_miniapp")
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, web_app=WebAppInfo(url=url))]]
    )

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
            await message.answer(
                t(user.language.value, "welcome_back", name=user.name),
                reply_markup=_webapp_kb(user.language.value),
            )
            inline = _webapp_inline(user.language.value)
            if inline:
                await message.answer(t(user.language.value, "open_mini_app"), reply_markup=inline)
            elif not settings.webapp_url:
                await message.answer(t(user.language.value, "webapp_url_missing"))
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
    lang = user.language.value if user else "uz"
    if not settings.webapp_url:
        await message.answer(t(lang, "webapp_url_missing"))
        return
    await message.answer(t(lang, "open_mini_app"), reply_markup=_webapp_kb(lang))
    inline = _webapp_inline(lang)
    if inline:
        await message.answer(t(lang, "or_this_button"), reply_markup=inline)


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
    lang = user.language.value if user else "uz"

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
        await callback.message.answer(t(lang, "search_check_app"))
        return

    await callback.answer()



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
            prefer_age_min=pref_min,
            prefer_age_max=pref_max,
            is_verified=False,  # keyinchalik yosh tasdiqlash bosqichi qo'shiladi
        )
        session.add(user)
        await session.commit()

    await state.clear()
    lang = data["language"].value if hasattr(data["language"], "value") else data["language"]
    await message.answer(
        t(lang, "reg_done", name=data["name"]),
        reply_markup=_webapp_kb(lang),
    )
    await message.answer(t(lang, "how_it_works"))
    inline = _webapp_inline(lang)
    if inline:
        await message.answer(t(lang, "open_mini_app"), reply_markup=inline)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    lang = user.language.value if user else "uz"
    await message.answer(t(lang, "how_it_works"), reply_markup=_webapp_kb(lang) if user else None)
    await message.answer(t(lang, "help_commands"))


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """
    Endi qidiruv va taklif jarayoni to'liq Mini App ichida bo'lganligi sababli,
    bu buyruq foydalanuvchini shunchaki Mini App'ga yo'naltiradi.
    """
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

    if not user:
        await message.answer(t("uz", "need_register"))
        return

    await message.answer(
        t(user.language.value, "search_check_app"),
        reply_markup=_webapp_kb(user.language.value),
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
    lang = user.language.value if user else "uz"
    await message.answer(t(lang, "stop_confirm"))


@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext):
    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if user:
            lang = user.language.value
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


@router.message(F.text)
async def fallback_text(message: Message, state: FSMContext):
    """Hech qaysi handler mos kelmasa — yo'l ko'rsatamiz."""
    current = await state.get_state()
    print(f"fallback: text={message.text!r} state={current}", flush=True)
    lang = "uz"
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
    if user:
        lang = user.language.value
    if current:
        await message.answer(t(lang, "bad_step"))
        return
    await message.answer(t(lang, "help_commands"), reply_markup=_webapp_kb(lang))
