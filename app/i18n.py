"""
Bot xabarlari uchun 3 tilli (uz/ru/en) matnlar lug'ati.
Foydalanuvchi ro'yxatdan o'tgandan keyingi barcha xabarlar shu orqali lokalizatsiya qilinadi.
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    "welcome_back": {
        "uz": "Xush kelibsiz qaytib, {name}!\nSuhbatdosh qidirish uchun pastdagi <b>Menu</b> tugmasini bosing, yoki /search buyrug'ini yuboring.",
        "ru": "С возвращением, {name}!\nЧтобы найти собеседника, нажмите кнопку <b>Menu</b> внизу или отправьте /search.",
        "en": "Welcome back, {name}!\nTap the <b>Menu</b> button below to find a chat partner, or send /search.",
    },
    "searching": {
        "uz": "Suhbatdosh qidirilmoqda... Bekor qilish uchun /stop yuboring.",
        "ru": "Ищем собеседника... Чтобы отменить, отправьте /stop.",
        "en": "Searching for a partner... Send /stop to cancel.",
    },
    "proposal_sent_notice": {
        "uz": "Sizga mos kishi topildi! Yuqoridagi xabarga javob bering.",
        "ru": "Найден подходящий собеседник! Ответьте на сообщение выше.",
        "en": "A match was found! Please respond to the message above.",
    },
    "proposal_text": {
        "uz": "🔔 Sizga mos suhbatdosh topildi!\n\nIsm: {name}\nYosh: {age}\nJins: {gender}\n\nShu kishi bilan suhbatlashishga rozimisiz?",
        "ru": "🔔 Найден подходящий собеседник!\n\nИмя: {name}\nВозраст: {age}\nПол: {gender}\n\nХотите пообщаться с этим человеком?",
        "en": "🔔 A match was found for you!\n\nName: {name}\nAge: {age}\nGender: {gender}\n\nWould you like to chat with this person?",
    },
    "btn_accept": {"uz": "✅ Roziman", "ru": "✅ Согласен(на)", "en": "✅ Accept"},
    "btn_decline": {"uz": "❌ Yo'q", "ru": "❌ Нет", "en": "❌ Decline"},
    "accepted_waiting_partner": {
        "uz": "✅ Siz rozi bo'ldingiz. Hamsuhbatingiz javobini kutmoqdamiz...",
        "ru": "✅ Вы согласились. Ждём ответа собеседника...",
        "en": "✅ You accepted. Waiting for the other person's response...",
    },
    "accepted_confirmed": {
        "uz": "✅ Siz rozi bo'ldingiz!",
        "ru": "✅ Вы согласились!",
        "en": "✅ You accepted!",
    },
    "match_started": {
        "uz": "🎉 Suhbat boshlandi!\nQo'ng'iroq uchun pastdagi tugmani bosing.",
        "ru": "🎉 Разговор начался!\nНажмите кнопку ниже, чтобы открыть звонок.",
        "en": "🎉 Chat started!\nTap the button below to open the call.",
    },
    "declined_self": {
        "uz": "❌ Siz rad etdingiz.",
        "ru": "❌ Вы отклонили.",
        "en": "❌ You declined.",
    },
    "declined_other": {
        "uz": "Afsuski, hamsuhbatingiz rad etdi. Sizni avtomatik ravishda qayta qidiruvga qo'shdik — kutib turing.",
        "ru": "К сожалению, собеседник отказался. Мы автоматически вернули вас в поиск — подождите.",
        "en": "Unfortunately, the other person declined. We've automatically put you back in the search queue — please wait.",
    },
    "proposal_invalid": {
        "uz": "Bu taklif eskirgan yoki allaqachon javob berilgan.",
        "ru": "Это предложение устарело или на него уже был дан ответ.",
        "en": "This proposal has expired or already been answered.",
    },
    "stop_confirm": {
        "uz": "Qidiruv/suhbat bekor qilindi. Qayta boshlash uchun /search.",
        "ru": "Поиск/разговор отменён. Чтобы начать заново, отправьте /search.",
        "en": "Search/chat cancelled. Send /search to start again.",
    },
    "partner_cancelled": {
        "uz": "Suhbatdoshingiz qidiruvni bekor qildi.",
        "ru": "Собеседник отменил поиск.",
        "en": "The other person cancelled the search.",
    },
    "reset_confirm": {
        "uz": "Profilingiz o'chirildi. Qayta ro'yxatdan o'tish uchun /start yuboring.",
        "ru": "Ваш профиль удалён. Отправьте /start, чтобы зарегистрироваться заново.",
        "en": "Your profile has been deleted. Send /start to register again.",
    },
    "gender_male": {"uz": "Erkak", "ru": "Мужской", "en": "Male"},
    "gender_female": {"uz": "Ayol", "ru": "Женский", "en": "Female"},
    "search_check_app": {
        "uz": "Qidiruv Mini App'da. Mini App ochiq bo'lsa taklif shu yerda; yopiq bo'lsa Telegramda xabar keladi.",
        "ru": "Поиск в Mini App. Если Mini App открыт — предложение там; если закрыт — придёт в Telegram.",
        "en": "Search in Mini App. If Mini App is open — proposal appears there; if closed — Telegram message.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    entry = TRANSLATIONS.get(key, {})
    template = entry.get(lang) or entry.get("uz") or key
    return template.format(**kwargs)


def gender_label(lang: str, gender: str) -> str:
    return t(lang, "gender_male" if gender == "male" else "gender_female")
