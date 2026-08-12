from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from app.bot.states import Registration
from app.config import settings
from app.database import async_session
from app.i18n import t
from app.matching.queue import cancel_proposals_by_user, cancel_wait, set_result
from app.models import Gender, Language, LookingFor, User

router = Router()


def _webapp_kb(lang: str = "uz") -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    """Mini App ochish tugmasi — video qo'ng'iroq shu yerda."""
    if not settings.webapp_url:
        print("WARNING: WEBAPP_URL bo'sh — Mini App tugmasi yuborilmaydi")
        return ReplyKeyboardRemove()
    label = {"uz": "🔍 Qidirish / Qo'ng'iroq", "ru": "🔍 Поиск / Звонок", "en": "🔍 Search / Call"}.get(
        lang, "🔍 Qidirish / Qo'ng'iroq"
    )
    url = f"{settings.webapp_url.rstrip('/')}/webapp/"
    print(f"Mini App URL: {url}")
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label, web_app=WebAppInfo(url=url))]],
        resize_keyboard=True,
    )

gender_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]],
    resize_keyboard=True,
)

language_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="O'zbek"), KeyboardButton(text="Русский"), KeyboardButton(text="English")]],
    resize_keyboard=True,
)

GENDER_MAP = {"Erkak": Gender.male, "Ayol": Gender.female}
OPPOSITE_GENDER = {Gender.male: LookingFor.female, Gender.female: LookingFor.male}
LANGUAGE_MAP = {"O'zbek": Language.uz, "Русский": Language.ru, "English": Language.en}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

    if user:
        await message.answer(
            t(user.language.value, "welcome_back", name=user.name),
            reply_markup=_webapp_kb(user.language.value),
        )
        return

    await message.answer("Salom! Ro'yxatdan o'tishni boshlaymiz.\nIsmingizni kiriting:")
    await state.set_state(Registration.name)


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
        await message.answer(f"Kechirasiz, bu botdan faqat {settings.min_age} yoshdan katta foydalanuvchilar foydalana oladi.")
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
    await message.answer("Qaysi tilda suhbatlashmoqchisiz?", reply_markup=language_kb)
    await state.set_state(Registration.language)


@router.message(Registration.language, F.text.in_(LANGUAGE_MAP.keys()))
async def process_language(message: Message, state: FSMContext):
    data = await state.update_data(language=LANGUAGE_MAP[message.text])

    async with async_session() as session:
        user = User(
            id=message.from_user.id,
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            looking_for=data["looking_for"],
            language=data["language"],
            is_verified=False,  # keyinchalik yosh tasdiqlash bosqichi qo'shiladi
        )
        session.add(user)
        await session.commit()

    await state.clear()
    lang = data["language"].value if hasattr(data["language"], "value") else data["language"]
    await message.answer(
        "✅ Ro'yxatdan o'tish tugadi!\n\n"
        "Suhbatdosh qidirish va <b>audio/video qo'ng'iroq</b> Mini App ichida.\n"
        "Pastdagi tugmani bosing yoki Menu → Qidirish.",
        reply_markup=_webapp_kb(lang),
    )


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """
    Endi qidiruv va taklif jarayoni to'liq Mini App ichida bo'lganligi sababli,
    bu buyruq foydalanuvchini shunchaki Mini App'ga yo'naltiradi.
    """
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

    if not user:
        await message.answer("Avval ro'yxatdan o'ting: /start")
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
        cancelled = await cancel_proposals_by_user(user.id)
        for proposal in cancelled:
            other_id = proposal["candidate_id"] if proposal["requester_id"] == user.id else proposal["requester_id"]
            await set_result(other_id, "requeued")

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
