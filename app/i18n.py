"""
Bot xabarlari — barcha tillar: uz/ru/en/de/tg/tr/ko/ja/zh/ar.
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    "welcome_back": {
        "uz": "Xush kelibsiz qaytib, {name}!\nSuhbatdosh qidirish uchun pastdagi <b>Menu → Qidirish</b> tugmasini bosing.",
        "ru": "С возвращением, {name}!\nЧтобы найти собеседника, нажмите <b>Menu → Поиск</b> внизу.",
        "en": "Welcome back, {name}!\nTap <b>Menu → Search</b> below to find a partner.",
        "de": "Willkommen zurück, {name}!\nTippen Sie unten auf <b>Menu → Suche</b>.",
        "tg": "Хуш омадед, {name}!\nБарои ҳамсуҳбат <b>Menu → Ҷустуҷӯ</b>-ро пахш кунед.",
        "tr": "Tekrar hoş geldiniz, {name}!\nPartner için alttaki <b>Menu → Ara</b> düğmesine basın.",
        "ko": "다시 오신 것을 환영합니다, {name}!\n상대를 찾으려면 아래 <b>Menu → 검색</b>을 누르세요.",
        "ja": "おかえりなさい、{name}!\n相手を探すには下の <b>Menu → 検索</b> をタップ。",
        "zh": "欢迎回来，{name}！\n点下方 <b>Menu → 搜索</b> 寻找聊天对象。",
        "ar": "مرحبًا بعودتك، {name}!\nللعثور على شريك اضغط <b>Menu → بحث</b> بالأسفل.",
    },
    "menu_btn": {
        "uz": "Qidirish", "ru": "Поиск", "en": "Search", "de": "Suche",
        "tg": "Ҷустуҷӯ", "tr": "Ara", "ko": "검색", "ja": "検索", "zh": "搜索",
        "ar": "بحث",
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
        "ar": "جاري البحث عن شريك... للإلغاء أرسل /stop.",
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
        "ar": "تم العثور على تطابق! الرجاء الرد على الرسالة أعلاه.",
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
        "ar": "🔔 تم العثور على شريك مناسب!\n\nالاسم: {name}\nالعمر: {age}\nالجنس: {gender}\n\nهل تريد الدردشة مع هذا الشخص؟",
    },
    "btn_accept": {
        "uz": "✅ Roziman", "ru": "✅ Согласен(на)", "en": "✅ Accept", "de": "✅ Annehmen",
        "tg": "✅ Розӣ", "tr": "✅ Kabul", "ko": "✅ 수락", "ja": "✅ 承諾", "zh": "✅ 接受",
        "ar": "✅ قبول",
    },
    "btn_decline": {
        "uz": "❌ Yo'q", "ru": "❌ Нет", "en": "❌ Decline", "de": "❌ Nein",
        "tg": "❌ Не", "tr": "❌ Hayır", "ko": "❌ 거절", "ja": "❌ 拒否", "zh": "❌ 拒绝",
        "ar": "❌ لا",
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
        "ar": "✅ قبلت. بانتظار رد الطرف الآخر...",
    },
    "accepted_confirmed": {
        "uz": "✅ Siz rozi bo'ldingiz!", "ru": "✅ Вы согласились!", "en": "✅ You accepted!",
        "de": "✅ Angenommen!", "tg": "✅ Розӣ шудед!", "tr": "✅ Kabul ettiniz!",
        "ko": "✅ 수락했습니다!", "ja": "✅ 承諾しました！", "zh": "✅ 已接受！",
        "ar": "✅ قبلت!",
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
        "ar": "🎉 بدأت المحادثة!\nافتح المكالمة بالزر أدناه.",
    },
    "declined_self": {
        "uz": "❌ Siz rad etdingiz.", "ru": "❌ Вы отклонили.", "en": "❌ You declined.",
        "de": "❌ Abgelehnt.", "tg": "❌ Рад кардед.", "tr": "❌ Reddettiniz.",
        "ko": "❌ 거절했습니다.", "ja": "❌ 拒否しました。", "zh": "❌ 已拒绝。",
        "ar": "❌ لقد رفضت.",
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
        "ar": "للأسف رفض الطرف الآخر. أعدنا إضافتك للبحث تلقائيًا — انتظر.",
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
        "ar": "هذا العرض منتهٍ أو تمت الإجابة عليه.",
    },
    "stop_confirm": {
        "uz": "Qidiruv/suhbat bekor qilindi. Qayta: <b>Menu → Qidirish</b>.",
        "ru": "Поиск/разговор отменён. Снова: <b>Menu → Поиск</b>.",
        "en": "Search/chat cancelled. Again: <b>Menu → Search</b>.",
        "de": "Suche/Chat abgebrochen. Erneut: <b>Menu → Suche</b>.",
        "tg": "Ҷустуҷӯ/суҳбат бекор. Аз нав: <b>Menu → Ҷустуҷӯ</b>.",
        "tr": "Arama/sohbet iptal. Yeniden: <b>Menu → Ara</b>.",
        "ko": "검색/채팅 취소됨. 다시: <b>Menu → 검색</b>.",
        "ja": "検索/チャットをキャンセル。再開は <b>Menu → 検索</b>。",
        "zh": "搜索/聊天已取消。重新开始：<b>Menu → 搜索</b>。",
        "ar": "أُلغي البحث/المحادثة. مجددًا: <b>Menu → بحث</b>.",
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
        "ar": "ألغى الشريك البحث.",
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
        "ar": "حُذف ملفك. للتسجيل مجددًا أرسل /start.",
    },
    "gender_male": {
        "uz": "Erkak", "ru": "Мужской", "en": "Male", "de": "Männlich",
        "tg": "Мард", "tr": "Erkek", "ko": "남성", "ja": "男性", "zh": "男",
        "ar": "ذكر",
    },
    "gender_female": {
        "uz": "Ayol", "ru": "Женский", "en": "Female", "de": "Weiblich",
        "tg": "Зан", "tr": "Kadın", "ko": "여성", "ja": "女性", "zh": "女",
        "ar": "أنثى",
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
        "ar": "سيظهر العرض في تطبيق الميني — اضغط Menu بالأسفل.",
    },

    "kb_search_call": {
        "uz": "🔍 Qidirish / Qo'ng'iroq", "ru": "🔍 Поиск / Звонок", "en": "🔍 Search / Call",
        "de": "🔍 Suche / Anruf", "tg": "🔍 Ҷустуҷӯ / Занг", "tr": "🔍 Arama / Görüşme",
        "ko": "🔍 검색 / 통화", "ja": "🔍 検索 / 通話", "zh": "🔍 搜索 / 通话",
        "ar": "🔍 بحث / مكالمة",
    },
    "kb_open_miniapp": {
        "uz": "📱 Mini Appni ochish", "ru": "📱 Открыть Mini App", "en": "📱 Open Mini App",
        "de": "📱 Mini App öffnen", "tg": "📱 Mini App-ро кушоед", "tr": "📱 Mini App'i aç",
        "ko": "📱 미니 앱 열기", "ja": "📱 ミニアプリを開く", "zh": "📱 打开迷你应用",
        "ar": "📱 افتح تطبيق الميني",
    },
    "open_mini_app": {
        "uz": "Mini Appni ochish:", "ru": "Открыть Mini App:", "en": "Open Mini App:",
        "de": "Mini App öffnen:", "tg": "Mini App-ро кушоед:", "tr": "Mini App'i açın:",
        "ko": "미니 앱 열기:", "ja": "ミニアプリを開く:", "zh": "打开迷你应用：",
        "ar": "افتح تطبيق الميني:",
    },
    "or_this_button": {
        "uz": "Yoki shu tugma:", "ru": "Или эта кнопка:", "en": "Or this button:",
        "de": "Oder dieser Button:", "tg": "Ё ин тугма:", "tr": "Veya bu düğme:",
        "ko": "또는 이 버튼:", "ja": "またはこのボタン:", "zh": "或此按钮：",
        "ar": "أو هذا الزر:",
    },
    "saved_call_invite": {
        "uz": "⭐ <b>{name}</b> ({age}, {gender}) siz bilan muloqot qilmoqchi.\n\nQo‘shilasizmi?",
        "ru": "⭐ <b>{name}</b> ({age}, {gender}) хочет пообщаться с вами.\n\nПрисоединитесь?",
        "en": "⭐ <b>{name}</b> ({age}, {gender}) wants to talk with you.\n\nJoin?",
        "de": "⭐ <b>{name}</b> ({age}, {gender}) möchte mit Ihnen sprechen.\n\nMitmachen?",
        "tg": "⭐ <b>{name}</b> ({age}, {gender}) бо шумо суҳбат кардан мехоҳад.\n\nҲамроҳ мешавед?",
        "tr": "⭐ <b>{name}</b> ({age}, {gender}) sizinle konuşmak istiyor.\n\nKatılır mısınız?",
        "ko": "⭐ <b>{name}</b> ({age}, {gender})님이 대화하고 싶어합니다.\n\n참여할까요?",
        "ja": "⭐ <b>{name}</b>（{age}・{gender}）が話したがっています。\n\n参加しますか？",
        "zh": "⭐ <b>{name}</b>（{age}，{gender}）想和你聊天。\n\n要加入吗？",
        "ar": "⭐ <b>{name}</b> ({age}, {gender}) يريد التحدث معك.\n\nهل تنضم؟",
    },
    "phone_request_ask": {
        "uz": "📱 <b>{name}</b> telefon raqamingizni so‘rayapti.\nUlashasizmi?",
        "ru": "📱 <b>{name}</b> просит ваш номер телефона.\nПоделиться?",
        "en": "📱 <b>{name}</b> is asking for your phone number.\nShare it?",
        "de": "📱 <b>{name}</b> fragt nach Ihrer Telefonnummer.\nTeilen?",
        "tg": "📱 <b>{name}</b> рақами телефони шуморо мепурсад.\nМедиҳед?",
        "tr": "📱 <b>{name}</b> telefon numaranızı istiyor.\nPaylaşır mısınız?",
        "ko": "📱 <b>{name}</b>님이 전화번호을 요청합니다.\n공유할까요?",
        "ja": "📱 <b>{name}</b> が電話番号を求めています。\n共有しますか？",
        "zh": "📱 <b>{name}</b> 正在请求你的电话号码。\n要分享吗？",
        "ar": "📱 <b>{name}</b> يطلب رقم هاتفك.\nهل تشاركه؟",
    },
    "phone_need_contact": {
        "uz": "Telefon raqamingizni yuboring — pastdagi tugmani bosing.",
        "ru": "Отправьте номер телефона — нажмите кнопку ниже.",
        "en": "Send your phone number — tap the button below.",
        "de": "Senden Sie Ihre Nummer — Button unten tippen.",
        "tg": "Рақами телефонро фиристед — тугмаи поён.",
        "tr": "Telefon numaranızı gönderin — alttaki düğme.",
        "ko": "전화번호를 보내세요 — 아래 버튼.",
        "ja": "電話番号を送ってください — 下のボタン。",
        "zh": "请发送你的电话号码 — 点下方按钮。",
        "ar": "أرسل رقم هاتفك — اضغط الزر أدناه.",
    },
    "btn_share_contact": {
        "uz": "📱 Raqamimni yuborish",
        "ru": "📱 Отправить номер",
        "en": "📱 Share my number",
        "de": "📱 Nummer teilen",
        "tg": "📱 Рақамро фиристодан",
        "tr": "📱 Numaramı gönder",
        "ko": "📱 번호 보내기",
        "ja": "📱 番号を送る",
        "zh": "📱 发送号码",
        "ar": "📱 إرسال رقمي",
    },
    "phone_shared": {
        "uz": "📱 Kontakt ulashildi\n\n<b>{name}</b>\n<code>{phone}</code>",
        "ru": "📱 Контакт получен\n\n<b>{name}</b>\n<code>{phone}</code>",
        "en": "📱 Contact shared\n\n<b>{name}</b>\n<code>{phone}</code>",
        "de": "📱 Kontakt geteilt\n\n<b>{name}</b>\n<code>{phone}</code>",
        "tg": "📱 Контакт\n\n<b>{name}</b>\n<code>{phone}</code>",
        "tr": "📱 İletişim paylaşıldı\n\n<b>{name}</b>\n<code>{phone}</code>",
        "ko": "📱 연락처 공유됨\n\n<b>{name}</b>\n<code>{phone}</code>",
        "ja": "📱 連絡先共有\n\n<b>{name}</b>\n<code>{phone}</code>",
        "zh": "📱 已分享联系方式\n\n<b>{name}</b>\n<code>{phone}</code>",
        "ar": "📱 تمت مشاركة جهة الاتصال\n\n<b>{name}</b>\n<code>{phone}</code>",
    },
    "phone_saved_thanks": {
        "uz": "✅ Raqamingiz saqlandi.",
        "ru": "✅ Номер сохранён.",
        "en": "✅ Number saved.",
        "de": "✅ Nummer gespeichert.",
        "tg": "✅ Рақам сабт шуд.",
        "tr": "✅ Numara kaydedildi.",
        "ko": "✅ 번호가 저장되었습니다.",
        "ja": "✅ 番号を保存しました。",
        "zh": "✅ 号码已保存。",
        "ar": "✅ تم حفظ الرقم.",
    },
    "webapp_url_missing": {
        "uz": "⚠️ WEBAPP_URL bo'sh. .env ni tekshiring.",
        "ru": "⚠️ WEBAPP_URL пуст. Проверьте .env.",
        "en": "⚠️ WEBAPP_URL is empty. Check .env.",
        "de": "⚠️ WEBAPP_URL ist leer. .env prüfen.",
        "tg": "⚠️ WEBAPP_URL холӣ. .env-ро санҷед.",
        "tr": "⚠️ WEBAPP_URL boş. .env'i kontrol edin.",
        "ko": "⚠️ WEBAPP_URL이 비어 있습니다. .env를 확인하세요.",
        "ja": "⚠️ WEBAPP_URL が空です。.env を確認してください。",
        "zh": "⚠️ WEBAPP_URL 为空。请检查 .env。",
        "ar": "⚠️ WEBAPP_URL فارغ. تحقق من .env.",
    },
    "reg_hello": {
        "uz": "Salom! <b>Soyla</b> — speaking, do‘st va juft topish.\n\n"
              "Ro‘yxat: ism → yosh → jins → til.\n"
              "Yoshga qat’iy chegara yo‘q.\n\n"
              "Ismingiz?",
        "ru": "Привет! <b>Soyla</b> — speaking, друзья и знакомства.\n\n"
              "Регистрация: имя → возраст → пол → язык.\n"
              "Жёсткого возрастного лимита нет.\n\n"
              "Как вас зовут?",
        "en": "Hi! <b>Soyla</b> — speaking, friends and dating.\n\n"
              "Sign up: name → age → gender → language.\n"
              "No hard age lock.\n\n"
              "What’s your name?",
        "de": "Hallo! <b>Soyla</b> — Speaking, Freunde und Dating.\n\n"
              "Registrierung: Name → Alter → Geschlecht → Sprache.\n"
              "Kein hartes Alterslimit.\n\n"
              "Ihr Name?",
        "tg": "Салом! <b>Soyla</b> — speaking, дӯст ва ҷуфт.\n\n"
              "Сабт: ном → синну сол → ҷинс → забон.\n"
              "Ҳадди қатъии синну сол нест.\n\n"
              "Номатон?",
        "tr": "Merhaba! <b>Soyla</b> — speaking, arkadaş ve eşleşme.\n\n"
              "Kayıt: ad → yaş → cinsiyet → dil.\n"
              "Katı yaş sınırı yok.\n\n"
              "Adınız?",
        "ko": "안녕하세요! <b>Soyla</b> — speaking, 친구, 소개팅.\n\n"
              "가입: 이름 → 나이 → 성별 → 언어.\n"
              "엄격한 나이 제한 없음.\n\n"
              "이름이 뭐예요?",
        "ja": "こんにちは！<b>Soyla</b> — speaking・友達・出会い。\n\n"
              "登録：名前→年齢→性別→言語。\n"
              "厳しい年齢制限はありません。\n\n"
              "お名前は？",
        "zh": "你好！<b>Soyla</b> — speaking、交友、配对。\n\n"
              "注册：姓名→年龄→性别→语言。\n"
              "没有硬性年龄限制。\n\n"
              "你叫什么？",
        "ar": "مرحبًا! <b>Soyla</b> — محادثة وأصدقاء وتعارف.\n\n"
              "التسجيل: الاسم → العمر → الجنس → اللغة.\n"
              "لا يوجد حد عمري صارم.\n\n"
              "ما اسمك؟",
    },
    "reg_done": {
        "uz": "✅ Tayyor, {name}!\nQidiruv: pastdagi <b>Menu → Qidirish</b>.",
        "ru": "✅ Готово, {name}!\nПоиск: <b>Menu → Поиск</b> внизу.",
        "en": "✅ You’re in, {name}!\nSearch: <b>Menu → Search</b> below.",
        "de": "✅ Fertig, {name}!\nSuche: <b>Menu → Suche</b> unten.",
        "tg": "✅ Тайёр, {name}!\nҶустуҷӯ: <b>Menu → Ҷустуҷӯ</b>.",
        "tr": "✅ Hazır, {name}!\nArama: alttaki <b>Menu → Ara</b>.",
        "ko": "✅ 준비됐어요, {name}!\n검색: 아래 <b>Menu → 검색</b>.",
        "ja": "✅ 準備OK、{name}!\n検索は下の <b>Menu → 検索</b>。",
        "zh": "✅ 好了，{name}！\n搜索：下方 <b>Menu → 搜索</b>。",
        "ar": "✅ جاهز، {name}!\nالبحث: <b>Menu → بحث</b> بالأسفل.",
    },
    "how_it_works": {
        "uz": "<b>Qanday ishlaydi</b> (qisqa):\n\n"
              "1) <b>Menu → Qidirish</b> ni bosing\n"
              "2) Katta tugmani bosing — qidiruv\n"
              "3) <b>Roziman</b> → video suhbat\n\n"
              "Aloqa tilini Mini Appdagi <b>Aloqa sozlamalari</b>da sozlang.\n"
              "Film nomi: botga ochiq silka yuboring (batafsil: /help).\n"
              "Yordam: /help",
        "ru": "<b>Как это работает</b>:\n\n"
              "1) Нажмите <b>Menu → Поиск</b>\n"
              "2) Большая кнопка — поиск\n"
              "3) <b>Согласен</b> → видеозвонок\n\n"
              "Язык общения — в <b>Параметрах общения</b>.\n"
              "Название фильма: пришлите открытую ссылку (подробнее: /help).\n"
              "Помощь: /help",
        "en": "<b>How it works</b>:\n\n"
              "1) Tap <b>Menu → Search</b>\n"
              "2) Tap the big button — search\n"
              "3) <b>Accept</b> → video call\n\n"
              "Set chat language in <b>Chat settings</b>.\n"
              "Movie title: send an open link (details: /help).\n"
              "Help: /help",
        "de": "<b>So geht’s</b>:\n\n"
              "1) <b>Menu → Suche</b> tippen\n"
              "2) Großen Button — Suche\n"
              "3) <b>Annehmen</b> → Videoanruf\n\n"
              "Chat-Sprache in den <b>Chat-Einstellungen</b>.\n"
              "Filmtitel: offenen Link senden (Details: /help).\n"
              "Hilfe: /help",
        "tg": "<b>Чӣ гуна кор мекунад</b>:\n\n"
              "1) <b>Menu → Ҷустуҷӯ</b>\n"
              "2) Тугмаи калон — ҷустуҷӯ\n"
              "3) <b>Розӣ</b> → видеозанг\n\n"
              "Забони суҳбат — дар <b>Танзимоти суҳбат</b>.\n"
              "Номи филм: пайванди кушода фиристед (/help).\n"
              "Ёрӣ: /help",
        "tr": "<b>Nasıl çalışır</b>:\n\n"
              "1) <b>Menu → Ara</b>\n"
              "2) Büyük düğme — arama\n"
              "3) <b>Kabul</b> → görüntülü sohbet\n\n"
              "Sohbet dili — <b>Sohbet ayarları</b>nda.\n"
              "Film adı: açık link gönderin (/help).\n"
              "Yardım: /help",
        "ko": "<b>사용 방법</b>:\n\n"
              "1) <b>Menu → 검색</b>\n"
              "2) 큰 버튼 — 검색\n"
              "3) <b>수락</b> → 영상 통화\n\n"
              "대화 언어는 <b>채팅 설정</b>에서.\n"
              "영화 제목: 공개 링크를 보내세요 (/help).\n"
              "도움말: /help",
        "ja": "<b>使い方</b>:\n\n"
              "1) <b>Menu → 検索</b>\n"
              "2) 大きなボタン — 検索\n"
              "3) <b>承諾</b> → ビデオ通話\n\n"
              "会話言語は<b>チャット設定</b>で。\n"
              "映画タイトル: 公開リンクを送る (/help)。\n"
              "ヘルプ: /help",
        "zh": "<b>怎么用</b>:\n\n"
              "1) 点 <b>Menu → 搜索</b>\n"
              "2) 点大按钮 — 搜索\n"
              "3) <b>接受</b> → 视频通话\n\n"
              "交流语言在<b>聊天设置</b>里。\n"
              "电影名：发送公开链接（详情 /help）。\n"
              "帮助: /help",
        "ar": "<b>كيف يعمل</b>:\n\n"
              "1) اضغط <b>Menu → بحث</b>\n"
              "2) الزر الكبير — بحث\n"
              "3) <b>قبول</b> → مكالمة فيديو\n\n"
              "لغة التواصل في <b>إعدادات التواصل</b>.\n"
              "اسم الفيلم: أرسل رابطاً عاماً (/help).\n"
              "المساعدة: /help",
    },
    "need_register": {
        "uz": "Avval ro'yxatdan o'ting: /start",
        "ru": "Сначала зарегистрируйтесь: /start",
        "en": "Please register first: /start",
        "de": "Bitte zuerst registrieren: /start",
        "tg": "Аввал сабт шавед: /start",
        "tr": "Önce kayıt olun: /start",
        "ko": "먼저 가입하세요: /start",
        "ja": "先に登録してください: /start",
        "zh": "请先注册：/start",
        "ar": "سجّل أولاً: /start",
    },
    "bad_step": {
        "uz": "Joriy bosqich uchun javob noto'g'ri. /start bilan boshidan.",
        "ru": "Неверный ответ для этого шага. Начните с /start.",
        "en": "Wrong reply for this step. Start over with /start.",
        "de": "Falsche Antwort. Neu mit /start.",
        "tg": "Ҷавоб нодуруст. Аз /start оғоз кунед.",
        "tr": "Bu adım için yanlış yanıt. /start ile baştan.",
        "ko": "이 단계에 잘못된 답변입니다. /start로 다시.",
        "ja": "この手順の返答が正しくありません。/start でやり直してください。",
        "zh": "此步骤回复不正确。请用 /start 重新开始。",
        "ar": "رد غير صحيح لهذه الخطوة. ابدأ من /start.",
    },
    "help_commands": {
        "uz": "Buyruqlar:\n/help — qanday ishlaydi\n/start — boshiga\n\nQidiruv: <b>Menu → Qidirish</b>\n\nFilm silkasini yuboring — kadr bo‘yicha internetdan nomini topaman (caption emas, fayl emas).",
        "ru": "Команды:\n/help — как это работает\n/start — в начало\n\nПоиск: <b>Menu → Поиск</b>\n\nПришлите ссылку на фильм — найду название в интернете по кадру (не подпись, не файл).",
        "en": "Commands:\n/help — how it works\n/start — restart\n\nSearch: <b>Menu → Search</b>\n\nSend a movie link — I’ll identify the title from the internet by the frame (not caption, not the file).",
        "de": "Befehle:\n/help — so geht’s\n/start — neu\n\nSuche: <b>Menu → Suche</b>\n\nFilm-Link senden — ich nenne den Titel (keine Datei).",
        "tg": "Фармонҳо:\n/help — чӣ гуна\n/start — аз аввал\n\nҶустуҷӯ: <b>Menu → Ҷустуҷӯ</b>\n\nПайванди филм фиристед — номро мегӯям (файл не).",
        "tr": "Komutlar:\n/help — nasıl çalışır\n/start — başa dön\n\nArama: <b>Menu → Ara</b>\n\nFilm linki gönderin — adını bulurum (dosya değil).",
        "ko": "명령:\n/help — 사용 방법\n/start — 처음으로\n\n검색: <b>Menu → 검색</b>\n\n영화 링크를 보내면 제목을 찾아드립니다 (파일 아님).",
        "ja": "コマンド:\n/help — 使い方\n/start — 最初から\n\n検索: <b>Menu → 検索</b>\n\n映画リンクを送るとタイトルを調べます（ファイルは送りません）。",
        "zh": "命令：\n/help — 怎么用\n/start — 重新开始\n\n搜索：<b>Menu → 搜索</b>\n\n发送电影链接 — 我会查找片名（不是文件）。",
        "ar": "الأوامر:\n/help — كيف يعمل\n/start — من البداية\n\nالبحث: <b>Menu → بحث</b>\n\nأرسل رابط فيلم — سأجد الاسم (وليس الملف).",
    },
    "link_looking": {
        "uz": "⏳ Qidiruv boshlandi…",
        "ru": "⏳ Поиск начался…",
        "en": "⏳ Search started…",
        "de": "⏳ Suche gestartet…",
        "tg": "⏳ Ҷустуҷӯ оғоз шуд…",
        "tr": "⏳ Arama başladı…",
        "ko": "⏳ 검색 시작…",
        "ja": "⏳ 検索開始…",
        "zh": "⏳ 开始搜索…",
        "ar": "⏳ بدأ البحث…",
    },
    "link_progress_download": {
        "uz": "⏳ Fayl olinmoqda…",
        "ru": "⏳ Получаю файл…",
        "en": "⏳ Downloading your file…",
        "de": "⏳ Datei wird geladen…",
        "tg": "⏳ Файл гирифта мешавад…",
        "tr": "⏳ Dosya alınıyor…",
        "ko": "⏳ 파일 받는 중…",
        "ja": "⏳ ファイル取得中…",
        "zh": "⏳ 正在获取文件…",
        "ar": "⏳ جاري جلب الملف…",
    },
    "link_progress_preview": {
        "uz": "⏳ Silkadagi preview rasm qidirilmoqda…",
        "ru": "⏳ Ищу превью по ссылке…",
        "en": "⏳ Fetching preview from the link…",
        "de": "⏳ Vorschaubild wird geladen…",
        "tg": "⏳ Превю ҷустуҷӯ…",
        "tr": "⏳ Önizleme aranıyor…",
        "ko": "⏳ 미리보기 가져오는 중…",
        "ja": "⏳ プレビュー取得中…",
        "zh": "⏳ 正在获取预览…",
        "ar": "⏳ جاري جلب المعاينة…",
    },
    "link_progress_auto_dl": {
        "uz": "⏳ Silkadagi video yuklanmoqda (faqat aniqlash)…",
        "ru": "⏳ Скачиваю видео по ссылке (только для распознавания)…",
        "en": "⏳ Fetching video from the link (identify only)…",
        "de": "⏳ Video wird geladen (nur Erkennung)…",
        "tg": "⏳ Видео аз истинод (танҳо шинохт)…",
        "tr": "⏳ Linkten video alınıyor (sadece tanıma)…",
        "ko": "⏳ 링크에서 영상 가져오는 중(식별만)…",
        "ja": "⏳ リンクから動画取得中（識別のみ）…",
        "zh": "⏳ 正在从链接获取视频（仅识别）…",
        "ar": "⏳ جاري جلب الفيديو من الرابط (للتعرّف فقط)…",
    },
    "link_progress_frame": {
        "uz": "⏳ Videodan kadr olinmoqda…",
        "ru": "⏳ Извлекаю кадр из видео…",
        "en": "⏳ Extracting a frame from the video…",
        "de": "⏳ Einzelbild wird extrahiert…",
        "tg": "⏳ Аз видео кадр…",
        "tr": "⏳ Videodan kare alınıyor…",
        "ko": "⏳ 영상에서 프레임 추출 중…",
        "ja": "⏳ 動画からフレーム抽出中…",
        "zh": "⏳ 正在截取视频帧…",
        "ar": "⏳ جاري استخراج إطار من الفيديو…",
    },
    "link_progress_ai": {
        "uz": "⏳ AI kadrni tahlil qilmoqda…",
        "ru": "⏳ ИИ анализирует кадр…",
        "en": "⏳ AI is analyzing the frame…",
        "de": "⏳ KI analysiert das Bild…",
        "tg": "⏳ AI кадрро таҳлил…",
        "tr": "⏳ AI kareyi analiz ediyor…",
        "ko": "⏳ AI가 프레임 분석 중…",
        "ja": "⏳ AIがフレームを分析中…",
        "zh": "⏳ AI 正在分析画面…",
        "ar": "⏳ الذكاء الاصطناعي يحلّل الإطار…",
    },
    "link_progress_search": {
        "uz": "⏳ Internetdan film qidirilmoqda…",
        "ru": "⏳ Ищу фильм в интернете…",
        "en": "⏳ Searching the internet for the movie…",
        "de": "⏳ Filmsuche im Internet…",
        "tg": "⏳ Дар интернет ҷустуҷӯи филм…",
        "tr": "⏳ İnternette film aranıyor…",
        "ko": "⏳ 인터넷에서 영화 검색 중…",
        "ja": "⏳ インターネットで映画検索中…",
        "zh": "⏳ 正在互联网搜索电影…",
        "ar": "⏳ جاري البحث عن الفيلم على الإنترنت…",
    },
    "link_progress_localize": {
        "uz": "⏳ Nom va qisqa mazmun tayyorlanmoqda…",
        "ru": "⏳ Готовлю название и краткое описание…",
        "en": "⏳ Preparing the title and short summary…",
        "de": "⏳ Titel und Kurzbeschreibung…",
        "tg": "⏳ Ном ва тавсифи кӯтоҳ…",
        "tr": "⏳ Ad ve kısa özet hazırlanıyor…",
        "ko": "⏳ 제목과 요약 준비 중…",
        "ja": "⏳ タイトルとあらすじを準備中…",
        "zh": "⏳ 正在准备片名和简介…",
        "ar": "⏳ جاري تجهيز الاسم والملخص…",
    },
    "link_found": {
        "uz": "🎬 <b>{title}</b>\n\n{summary}",
        "ru": "🎬 <b>{title}</b>\n\n{summary}",
        "en": "🎬 <b>{title}</b>\n\n{summary}",
        "de": "🎬 <b>{title}</b>\n\n{summary}",
        "tg": "🎬 <b>{title}</b>\n\n{summary}",
        "tr": "🎬 <b>{title}</b>\n\n{summary}",
        "ko": "🎬 <b>{title}</b>\n\n{summary}",
        "ja": "🎬 <b>{title}</b>\n\n{summary}",
        "zh": "🎬 <b>{title}</b>\n\n{summary}",
        "ar": "🎬 <b>{title}</b>\n\n{summary}",
    },
    "link_found_uncertain": {
        "uz": "Kechirasiz — bu ma’lumot bo‘yicha aniq <b>bitta</b> filmni topa olmadim.\n\n"
              "Yaqinroq taxminlar:\n{list}\n\n"
              "Qaysi biri to‘g‘ri? Aniqroq screenshot yoki qisqa video yuboring.",
        "ru": "Извините — по этим данным не нашёл <b>один</b> точный фильм.\n\n"
              "Близкие варианты:\n{list}\n\n"
              "Какой верный? Пришлите более чёткий кадр или короткое видео.",
        "en": "Sorry — I couldn’t find <b>one</b> exact movie from that.\n\n"
              "Closest guesses:\n{list}\n\n"
              "Which is right? Send a clearer screenshot or short clip.",
        "de": "Entschuldigung — keinen <b>einzigen</b> genauen Film gefunden.\n\n"
              "Nächste Treffer:\n{list}\n\n"
              "Welcher stimmt? Klareren Screenshot oder kurzen Clip senden.",
        "tg": "Бубахшед — як филми аниқ ёфт нашуд.\n\n"
              "Тахминҳо:\n{list}\n\n"
              "Кадомаш дуруст? Screenshot ё клип.",
        "tr": "Üzgünüm — net <b>tek</b> filmi bulamadım.\n\n"
              "Yakın tahminler:\n{list}\n\n"
              "Hangisi doğru? Daha net ekran görüntüsü veya kısa klip.",
        "ko": "죄송해요 — 정확한 <b>한 편</b>을 찾지 못했어요.\n\n"
              "가까운 추측:\n{list}\n\n"
              "맞는 작품이 있나요? 더 선명한 스크린샷이나 짧은 클립을 보내주세요.",
        "ja": "すみません — 正確な<b>1本</b>を特定できませんでした。\n\n"
              "近い候補:\n{list}\n\n"
              "正しいものは？より鮮明なスクショか短い動画を。",
        "zh": "抱歉 — 无法根据这些信息找到<b>唯一</b>准确片名。\n\n"
              "较接近的猜测：\n{list}\n\n"
              "哪一部对？请发更清晰的截图或短视频。",
        "ar": "عذراً — لم أجد فيلماً <b>واحداً</b> بدقة من هذه البيانات.\n\n"
              "أقرب التخمينات:\n{list}\n\n"
              "أيّها الصحيح؟ أرسل لقطة أوضح أو مقطعاً قصيراً.",
    },
    "link_not_found": {
        "uz": "Kechirasiz — bu ma’lumot bo‘yicha aniq filmni topa olmadim.\n\n"
              "Aniqroq <b>screenshot</b> yoki qisqa <b>video</b> (20 MB gacha) yuboring — yana qidiraman.",
        "ru": "Извините — по этим данным точный фильм не нашёл.\n\n"
              "Пришлите более чёткий <b>скриншот</b> или короткое <b>видео</b> (до 20 МБ).",
        "en": "Sorry — I couldn’t find the exact movie from that.\n\n"
              "Send a clearer <b>screenshot</b> or short <b>video</b> (up to 20 MB).",
        "de": "Entschuldigung — den genauen Film konnte ich nicht finden.\n\n"
              "Klareren <b>Screenshot</b> oder kurzes <b>Video</b> (max. 20 MB) senden.",
        "tg": "Бубахшед — филми аниқ ёфт нашуд.\n\n"
              "Screenshot ё клипи кӯтоҳ (то 20 МБ) фиристед.",
        "tr": "Üzgünüm — net filmi bulamadım.\n\n"
              "Daha net <b>ekran görüntüsü</b> veya kısa <b>video</b> (20 MB) gönderin.",
        "ko": "죄송해요 — 정확한 영화를 찾지 못했어요.\n\n"
              "더 선명한 <b>스크린샷</b>이나 짧은 <b>영상</b>(20MB)을 보내주세요.",
        "ja": "すみません — 正確な映画を特定できませんでした。\n\n"
              "より鮮明な<b>スクショ</b>か短い<b>動画</b>（最大20MB）を送ってください。",
        "zh": "抱歉 — 无法根据这些信息找到准确片名。\n\n"
              "请发送更清晰的<b>截图</b>或短<b>视频</b>（最大20MB）。",
        "ar": "عذراً — لم أجد الفيلم بدقة من هذه البيانات.\n\n"
              "أرسل <b>لقطة أوضح</b> أو <b>مقطعاً قصيراً</b> (حتى 20MB).",
    },
    "link_need_gemini": {
        "uz": "Kechirasiz — hozircha kadrni tahlil qila olmadim.\n\n"
              "Aniqroq screenshot yoki qisqa video yuboring.",
        "ru": "Извините — сейчас не удалось разобрать кадр.\n\n"
              "Пришлите более чёткий скриншот или короткое видео.",
        "en": "Sorry — I couldn’t analyze the frame right now.\n\n"
              "Send a clearer screenshot or short video.",
        "de": "Entschuldigung — Bildanalyse gerade nicht möglich.\n\n"
              "Klareren Screenshot oder kurzen Clip senden.",
        "tg": "Бубахшед — кадрро таҳлил карда натавонистам.\n\nScreenshot ё клип.",
        "tr": "Üzgünüm — kareyi şu an analiz edemedim.\n\nDaha net ekran görüntüsü veya kısa klip.",
        "ko": "죄송해요 — 지금 프레임을 분석하지 못했어요.\n\n더 선명한 스크린샷이나 짧은 클립을 보내주세요.",
        "ja": "すみません — 今フレームを分析できませんでした。\n\nより鮮明なスクショか短い動画を。",
        "zh": "抱歉 — 暂时无法分析画面。\n\n请发送更清晰的截图或短视频。",
        "ar": "عذراً — تعذّر تحليل الإطار الآن.\n\nأرسل لقطة أوضح أو مقطعاً قصيراً.",
    },
    "link_need_preview": {
        "uz": "Kechirasiz — silkadagi kadrni ochib bo‘lmadi.\n\n"
              "Videoni o‘zingiz yuboring (20 MB gacha) yoki aniqroq <b>screenshot</b> tashlang.",
        "ru": "Извините — не удалось открыть кадр по ссылке.\n\n"
              "Пришлите само видео (до 20 МБ) или более чёткий <b>скриншот</b>.",
        "en": "Sorry — couldn’t open a frame from that link.\n\n"
              "Send the video yourself (up to 20 MB) or a clearer <b>screenshot</b>.",
        "de": "Entschuldigung — kein Bild aus dem Link.\n\n"
              "Video selbst senden (max. 20 MB) oder klareren Screenshot.",
        "tg": "Бубахшед — аз истинод кадр кушода нашуд.\n\nВидео ё screenshot.",
        "tr": "Üzgünüm — linkten kare açılamadı.\n\nVideoyu kendiniz (20 MB) veya net ekran görüntüsü gönderin.",
        "ko": "죄송해요 — 링크에서 프레임을 열 수 없어요.\n\n영상(20MB)이나 더 선명한 스크린샷을 보내주세요.",
        "ja": "すみません — リンクからフレームを取得できませんでした。\n\n動画（最大20MB）か鮮明なスクショを。",
        "zh": "抱歉 — 无法从链接打开画面。\n\n请直接发送视频（最大20MB）或更清晰的截图。",
        "ar": "عذراً — تعذّر فتح إطار من الرابط.\n\nأرسل الفيديو بنفسك (حتى 20MB) أو لقطة أوضح.",
    },
    "link_video_too_large": {
        "uz": "Video juda katta (maks. ~20 MB). Qisqaroq klip yoki screenshot yuboring.\n\n<i>Faqat nom — video saqlanmaydi.</i>",
        "ru": "Видео слишком большое (макс. ~20 МБ). Пришлите короткий клип или скрин.\n\n<i>Только название.</i>",
        "en": "Video is too large (max ~20 MB). Send a short clip or screenshot.\n\n<i>Title only.</i>",
        "de": "Video zu groß (max. ~20 MB). Kurzer Clip oder Screenshot.",
        "tg": "Видео калон (~20 МБ). Клип ё screenshot.",
        "tr": "Video çok büyük (~20 MB). Kısa klip veya ekran görüntüsü.",
        "ko": "영상이 너무 큽니다(~20MB). 짧은 클립 또는 스크린샷.",
        "ja": "動画が大きすぎます（最大約20MB）。短いクリップかスクショを。",
        "zh": "视频太大（最大约20MB）。请发短片段或截图。",
        "ar": "الفيديو كبير جداً (~20MB). أرسل مقطعاً قصيراً أو لقطة شاشة.",
    },
    "link_guide": {
        "uz": "<b>🎬 Film nomini silka orqali topish</b>\n\n"
              "<b>Qanday:</b>\n"
              "1) Instagram/TikTok/YouTube silkasini botga yuboring\n"
              "2) Bot postdagi <b>kadr/preview</b> ni oladi\n"
              "3) Shu rasm bo‘yicha <b>internetdan</b> filmni qidiradi\n"
              "4) Topilsa haqiqiy nom chiqadi\n\n"
              "<b>Muhim:</b> post caption/tavsifi o‘qilmaydi — internet/AI qidiruv.\n"
              "Instagram/TikTok uchun <b>GEMINI_API_KEY</b> kerak (.env).\n"
              "Yopiq postlar yoki rasm chiqmasa ishlamasligi mumkin.\n\n"
              "<i>Faqat nom — film fayli yuborilmaydi.</i>",
        "ru": "<b>🎬 Название фильма по ссылке</b>\n\n"
              "1) Пришлите ссылку Instagram/TikTok/YouTube\n"
              "2) Бот берёт <b>кадр/превью</b>\n"
              "3) Ищет фильм <b>в интернете/AI</b> по изображению\n"
              "4) Показывает настоящее название\n\n"
              "<b>Важно:</b> подпись поста не используется.\n"
              "Для Instagram/TikTok нужен <b>GEMINI_API_KEY</b>.\n\n"
              "<i>Только название — файл не отправляется.</i>",
        "en": "<b>🎬 Find a movie title from a link</b>\n\n"
              "1) Send an Instagram/TikTok/YouTube link\n"
              "2) Bot takes the <b>preview frame</b>\n"
              "3) Searches the <b>internet/AI</b> by that image\n"
              "4) Returns the real movie title\n\n"
              "<b>Important:</b> post captions are not used as the answer.\n"
              "Instagram/TikTok needs <b>GEMINI_API_KEY</b> in .env.\n\n"
              "<i>Title only — no file is sent.</i>",
        "de": "<b>🎬 Filmtitel aus Link</b>\n\n"
              "Vorschau-Bild → Internetsuche → Filmtitel.\n"
              "Caption wird nicht als Antwort genutzt.\n\n"
              "<i>Nur Titel — keine Datei.</i>",
        "tg": "<b>🎬 Номи филм аз пайванд</b>\n\n"
              "Кадр → ҷустуҷӯи интернет → номи филм.\n"
              "Тавсифи пост ҷавоб нест.\n\n"
              "<i>Танҳо ном.</i>",
        "tr": "<b>🎬 Linkten film adı</b>\n\n"
              "Önizleme karesi → internet araması → film adı.\n"
              "Caption cevap olarak kullanılmaz.\n\n"
              "<i>Sadece ad.</i>",
        "ko": "<b>🎬 링크로 영화 제목</b>\n\n"
              "미리보기 프레임 → 인터넷 검색 → 영화 제목.\n"
              "캡션은 답으로 쓰지 않습니다.\n\n"
              "<i>제목만.</i>",
        "ja": "<b>🎬 リンクから映画タイトル</b>\n\n"
              "プレビュー画像 → ネット検索 → 映画タイトル。\n"
              "キャプションは答えに使いません。\n\n"
              "<i>タイトルのみ。</i>",
        "zh": "<b>🎬 用链接查电影名</b>\n\n"
              "预览画面 → 互联网搜索 → 电影名。\n"
              "不使用帖子说明作为答案。\n\n"
              "<i>仅片名。</i>",
        "ar": "<b>🎬 اسم الفيلم من الرابط</b>\n\n"
              "إطار المعاينة → بحث إنترنت → اسم الفيلم.\n"
              "لا نستخدم وصف المنشور كإجابة.\n\n"
              "<i>الاسم فقط.</i>",
    },

}


def t(lang: str, key: str, **kwargs) -> str:
    entry = TRANSLATIONS.get(key, {})
    template = entry.get(lang) or entry.get("en") or entry.get("uz") or key
    return template.format(**kwargs)


def gender_label(lang: str, gender: str) -> str:
    return t(lang, "gender_male" if gender == "male" else "gender_female")
