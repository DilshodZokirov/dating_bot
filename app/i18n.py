"""
Bot xabarlari — barcha tillar: uz/ru/en/de/tg/tr/ko/ja/zh.
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    "welcome_back": {
        "uz": "Xush kelibsiz qaytib, {name}!\nSuhbatdosh qidirish uchun pastdagi <b>Menu</b> tugmasini bosing, yoki /search buyrug'ini yuboring.",
        "ru": "С возвращением, {name}!\nЧтобы найти собеседника, нажмите кнопку <b>Menu</b> внизу или отправьте /search.",
        "en": "Welcome back, {name}!\nTap the <b>Menu</b> button below to find a chat partner, or send /search.",
        "de": "Willkommen zurück, {name}!\nTippen Sie unten auf <b>Menu</b> oder senden Sie /search.",
        "tg": "Хуш омадед, {name}!\nБарои ёфтани ҳамсуҳбат <b>Menu</b>-ро пахш кунед ё /search фиристед.",
        "tr": "Tekrar hoş geldiniz, {name}!\nPartner bulmak için <b>Menu</b> veya /search.",
        "ko": "다시 오신 것을 환영합니다, {name}!\n상대를 찾으려면 <b>Menu</b> 또는 /search.",
        "ja": "おかえりなさい、{name}!\n相手を探すには <b>Menu</b> か /search。",
        "zh": "欢迎回来，{name}！\n点下方 <b>Menu</b> 或发送 /search 寻找聊天对象。",
    },
    "searching": {
        "uz": "Suhbatdosh qidirilmoqda... Bekor qilish uchun /stop yuboring.",
        "ru": "Ищем собеседника... Чтобы отменить, отправьте /stop.",
        "en": "Searching for a partner... Send /stop to cancel.",
        "de": "Suche Partner... /stop zum Abbrechen.",
        "tg": "Ҳамсуҳбат ҷустуҷӯ... /stop барои бекор.",
        "tr": "Partner aranıyor... İptal: /stop.",
        "ko": "상대 검색 중... 취소: /stop.",
        "ja": "相手を検索中... キャンセルは /stop。",
        "zh": "正在寻找对象… 取消请发 /stop。",
    },
    "proposal_sent_notice": {
        "uz": "Sizga mos kishi topildi! Yuqoridagi xabarga javob bering.",
        "ru": "Найден подходящий собеседник! Ответьте на сообщение выше.",
        "en": "A match was found! Please respond to the message above.",
        "de": "Ein Match wurde gefunden! Bitte oben antworten.",
        "tg": "Шахси мувофиқ ёфт шуд! Ба паёми боло ҷавоб диҳед.",
        "tr": "Eşleşme bulundu! Yukarıdaki mesaja yanıt verin.",
        "ko": "매칭을 찾았습니다! 위 메시지에 답하세요.",
        "ja": "マッチが見つかりました！上のメッセージに返信してください。",
        "zh": "找到匹配了！请回复上方消息。",
    },
    "proposal_text": {
        "uz": "🔔 Sizga mos suhbatdosh topildi!\n\nIsm: {name}\nYosh: {age}\nJins: {gender}\n\nShu kishi bilan suhbatlashishga rozimisiz?",
        "ru": "🔔 Найден подходящий собеседник!\n\nИмя: {name}\nВозраст: {age}\nПол: {gender}\n\nХотите пообщаться с этим человеком?",
        "en": "🔔 A match was found for you!\n\nName: {name}\nAge: {age}\nGender: {gender}\n\nWould you like to chat with this person?",
        "de": "🔔 Ein Match!\n\nName: {name}\nAlter: {age}\nGeschlecht: {gender}\n\nMöchten Sie chatten?",
        "tg": "🔔 Ҳамсуҳбати мувофиқ!\n\nНом: {name}\nСинну сол: {age}\nҶинс: {gender}\n\nСуҳбат мекунед?",
        "tr": "🔔 Eşleşme bulundu!\n\nİsim: {name}\nYaş: {age}\nCinsiyet: {gender}\n\nSohbet etmek ister misiniz?",
        "ko": "🔔 매칭을 찾았습니다!\n\n이름: {name}\n나이: {age}\n성별: {gender}\n\n대화할까요?",
        "ja": "🔔 マッチです！\n\n名前: {name}\n年齢: {age}\n性別: {gender}\n\n話しますか？",
        "zh": "🔔 为你找到匹配！\n\n姓名：{name}\n年龄：{age}\n性别：{gender}\n\n要聊天吗？",
    },
    "btn_accept": {
        "uz": "✅ Roziman", "ru": "✅ Согласен(на)", "en": "✅ Accept", "de": "✅ Annehmen",
        "tg": "✅ Розӣ", "tr": "✅ Kabul", "ko": "✅ 수락", "ja": "✅ 承諾", "zh": "✅ 接受",
    },
    "btn_decline": {
        "uz": "❌ Yo'q", "ru": "❌ Нет", "en": "❌ Decline", "de": "❌ Nein",
        "tg": "❌ Не", "tr": "❌ Hayır", "ko": "❌ 거절", "ja": "❌ 拒否", "zh": "❌ 拒绝",
    },
    "accepted_waiting_partner": {
        "uz": "✅ Siz rozi bo'ldingiz. Hamsuhbatingiz javobini kutmoqdamiz...",
        "ru": "✅ Вы согласились. Ждём ответа собеседника...",
        "en": "✅ You accepted. Waiting for the other person's response...",
        "de": "✅ Angenommen. Warte auf die andere Person...",
        "tg": "✅ Шумо розӣ шудед. Ҷавобро интизорем...",
        "tr": "✅ Kabul ettiniz. Partner bekleniyor...",
        "ko": "✅ 수락했습니다. 상대 응답 대기 중...",
        "ja": "✅ 承諾しました。相手を待っています...",
        "zh": "✅ 已接受。正在等待对方…",
    },
    "accepted_confirmed": {
        "uz": "✅ Siz rozi bo'ldingiz!", "ru": "✅ Вы согласились!", "en": "✅ You accepted!",
        "de": "✅ Angenommen!", "tg": "✅ Розӣ шудед!", "tr": "✅ Kabul ettiniz!",
        "ko": "✅ 수락했습니다!", "ja": "✅ 承諾しました！", "zh": "✅ 已接受！",
    },
    "match_started": {
        "uz": "🎉 Suhbat boshlandi!\nQo'ng'iroq uchun pastdagi tugmani bosing.",
        "ru": "🎉 Разговор начался!\nНажмите кнопку ниже, чтобы открыть звонок.",
        "en": "🎉 Chat started!\nTap the button below to open the call.",
        "de": "🎉 Chat gestartet!\nTippen Sie unten, um den Anruf zu öffnen.",
        "tg": "🎉 Суҳбат оғоз шуд!\nБарои занг тугмаи поёнро пахш кунед.",
        "tr": "🎉 Sohbet başladı!\nAramayı açmak için alttaki düğmeye basın.",
        "ko": "🎉 대화가 시작되었습니다!\n아래 버튼으로 통화를 여세요.",
        "ja": "🎉 チャット開始！\n下のボタンで通話を開いてください。",
        "zh": "🎉 聊天开始！\n点下方按钮打开通话。",
    },
    "declined_self": {
        "uz": "❌ Siz rad etdingiz.", "ru": "❌ Вы отклонили.", "en": "❌ You declined.",
        "de": "❌ Abgelehnt.", "tg": "❌ Рад кардед.", "tr": "❌ Reddettiniz.",
        "ko": "❌ 거절했습니다.", "ja": "❌ 拒否しました。", "zh": "❌ 已拒绝。",
    },
    "declined_other": {
        "uz": "Afsuski, hamsuhbatingiz rad etdi. Sizni avtomatik ravishda qayta qidiruvga qo'shdik — kutib turing.",
        "ru": "К сожалению, собеседник отказался. Мы автоматически вернули вас в поиск — подождите.",
        "en": "Unfortunately, the other person declined. We've automatically put you back in the search queue — please wait.",
        "de": "Leider abgelehnt. Sie sind wieder in der Suche — bitte warten.",
        "tg": "Мутаассифона рад шуд. Шумо боз дар ҷустуҷӯ ҳастед — интизор шавед.",
        "tr": "Maalesef reddedildi. Tekrar aramadasınız — bekleyin.",
        "ko": "상대가 거절했습니다. 다시 검색 중입니다 — 잠시만요.",
        "ja": "残念ながら拒否されました。再検索中です — お待ちください。",
        "zh": "对方已拒绝。已自动重新加入搜索 — 请稍候。",
    },
    "proposal_invalid": {
        "uz": "Bu taklif eskirgan yoki allaqachon javob berilgan.",
        "ru": "Это предложение устарело или на него уже был дан ответ.",
        "en": "This proposal has expired or already been answered.",
        "de": "Dieser Vorschlag ist abgelaufen oder bereits beantwortet.",
        "tg": "Ин таклиф кӯҳна ё аллакай ҷавоб дода шудааст.",
        "tr": "Bu teklif süresi dolmuş veya yanıtlanmış.",
        "ko": "이 제안은 만료되었거나 이미 응답되었습니다.",
        "ja": "この提案は期限切れか、すでに回答済みです。",
        "zh": "该提议已过期或已回复。",
    },
    "stop_confirm": {
        "uz": "Qidiruv/suhbat bekor qilindi. Qayta boshlash uchun /search.",
        "ru": "Поиск/разговор отменён. Чтобы начать заново, отправьте /search.",
        "en": "Search/chat cancelled. Send /search to start again.",
        "de": "Suche/Chat abgebrochen. /search zum Neustart.",
        "tg": "Ҷустуҷӯ/суҳбат бекор. Аз нав: /search.",
        "tr": "Arama/sohbet iptal. Yeniden: /search.",
        "ko": "검색/채팅 취소됨. 다시: /search.",
        "ja": "検索/チャットをキャンセル。再開は /search。",
        "zh": "搜索/聊天已取消。重新开始请发 /search。",
    },
    "partner_cancelled": {
        "uz": "Suhbatdoshingiz qidiruvni bekor qildi.",
        "ru": "Собеседник отменил поиск.",
        "en": "The other person cancelled the search.",
        "de": "Die andere Person hat die Suche abgebrochen.",
        "tg": "Ҳамсуҳбат ҷустуҷӯро бекор кард.",
        "tr": "Partner aramayı iptal etti.",
        "ko": "상대가 검색을 취소했습니다.",
        "ja": "相手が検索をキャンセルしました。",
        "zh": "对方取消了搜索。",
    },
    "reset_confirm": {
        "uz": "Profilingiz o'chirildi. Qayta ro'yxatdan o'tish uchun /start yuboring.",
        "ru": "Ваш профиль удалён. Отправьте /start, чтобы зарегистрироваться заново.",
        "en": "Your profile has been deleted. Send /start to register again.",
        "de": "Profil gelöscht. /start zur Neu-Registrierung.",
        "tg": "Профил нест шуд. Аз нав: /start.",
        "tr": "Profil silindi. Yeniden kayıt: /start.",
        "ko": "프로필이 삭제되었습니다. 재가입: /start.",
        "ja": "プロフィールを削除しました。再登録は /start。",
        "zh": "资料已删除。重新注册请发 /start。",
    },
    "gender_male": {
        "uz": "Erkak", "ru": "Мужской", "en": "Male", "de": "Männlich",
        "tg": "Мард", "tr": "Erkek", "ko": "남성", "ja": "男性", "zh": "男",
    },
    "gender_female": {
        "uz": "Ayol", "ru": "Женский", "en": "Female", "de": "Weiblich",
        "tg": "Зан", "tr": "Kadın", "ko": "여성", "ja": "女性", "zh": "女",
    },
    "search_check_app": {
        "uz": "Taklif Mini App'da ko'rinadi — pastdagi Menu tugmasini bosing.",
        "ru": "Предложение появится в Mini App — нажмите кнопку Menu внизу.",
        "en": "The proposal will appear in the Mini App — tap the Menu button below.",
        "de": "Der Vorschlag erscheint in der Mini App — tippen Sie auf Menu.",
        "tg": "Таклиф дар Mini App — Menu-ро пахш кунед.",
        "tr": "Teklif Mini App'te görünür — Menu'ye basın.",
        "ko": "제안이 미니 앱에 표시됩니다 — Menu를 누르세요.",
        "ja": "提案はミニアプリに表示されます — Menu をタップ。",
        "zh": "提议会出现在迷你应用中 — 请点 Menu。",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    entry = TRANSLATIONS.get(key, {})
    template = entry.get(lang) or entry.get("en") or entry.get("uz") or key
    return template.format(**kwargs)


def gender_label(lang: str, gender: str) -> str:
    return t(lang, "gender_male" if gender == "male" else "gender_female")
