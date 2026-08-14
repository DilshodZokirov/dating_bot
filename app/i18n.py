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
        "uz": "Salom! <b>Soyla</b> — suhbatdosh topib, video qo‘ng‘iroq.\n\nIsmingiz?",
        "ru": "Привет! <b>Soyla</b> — найти собеседника и видеозвонок.\n\nКак вас зовут?",
        "en": "Hi! <b>Soyla</b> — find a partner and jump on a video call.\n\nWhat’s your name?",
        "de": "Hallo! <b>Soyla</b> — Partner finden und Videoanruf.\n\nIhr Name?",
        "tg": "Салом! <b>Soyla</b> — ҳамсуҳбат ва видеозанг.\n\nНоматон?",
        "tr": "Merhaba! <b>Soyla</b> — eşleşme bul, görüntülü ara.\n\nAdınız?",
        "ko": "안녕하세요! <b>Soyla</b> — 상대를 찾고 영상 통화.\n\n이름이 뭐예요?",
        "ja": "こんにちは！<b>Soyla</b> — 相手を見つけてビデオ通話。\n\nお名前は？",
        "zh": "你好！<b>Soyla</b> — 找到聊天对象并视频通话。\n\n你叫什么？",
        "ar": "مرحبًا! <b>Soyla</b> — اعثر على شريك وابدأ مكالمة فيديو.\n\nما اسمك؟",
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
              "Yordam: /help",
        "ru": "<b>Как это работает</b>:\n\n"
              "1) Нажмите <b>Menu → Поиск</b>\n"
              "2) Большая кнопка — поиск\n"
              "3) <b>Согласен</b> → видеозвонок\n\n"
              "Язык общения — в <b>Параметрах общения</b>.\n"
              "Помощь: /help",
        "en": "<b>How it works</b>:\n\n"
              "1) Tap <b>Menu → Search</b>\n"
              "2) Tap the big button — search\n"
              "3) <b>Accept</b> → video call\n\n"
              "Set chat language in <b>Chat settings</b>.\n"
              "Help: /help",
        "de": "<b>So geht’s</b>:\n\n"
              "1) <b>Menu → Suche</b> tippen\n"
              "2) Großen Button — Suche\n"
              "3) <b>Annehmen</b> → Videoanruf\n\n"
              "Chat-Sprache in den <b>Chat-Einstellungen</b>.\n"
              "Hilfe: /help",
        "tg": "<b>Чӣ гуна кор мекунад</b>:\n\n"
              "1) <b>Menu → Ҷустуҷӯ</b>\n"
              "2) Тугмаи калон — ҷустуҷӯ\n"
              "3) <b>Розӣ</b> → видеозанг\n\n"
              "Забони суҳбат — дар <b>Танзимоти суҳбат</b>.\n"
              "Ёрӣ: /help",
        "tr": "<b>Nasıl çalışır</b>:\n\n"
              "1) <b>Menu → Ara</b>\n"
              "2) Büyük düğme — arama\n"
              "3) <b>Kabul</b> → görüntülü sohbet\n\n"
              "Sohbet dili — <b>Sohbet ayarları</b>nda.\n"
              "Yardım: /help",
        "ko": "<b>사용 방법</b>:\n\n"
              "1) <b>Menu → 검색</b>\n"
              "2) 큰 버튼 — 검색\n"
              "3) <b>수락</b> → 영상 통화\n\n"
              "대화 언어는 <b>채팅 설정</b>에서.\n"
              "도움말: /help",
        "ja": "<b>使い方</b>:\n\n"
              "1) <b>Menu → 検索</b>\n"
              "2) 大きなボタン — 検索\n"
              "3) <b>承諾</b> → ビデオ通話\n\n"
              "会話言語は<b>チャット設定</b>で。\n"
              "ヘルプ: /help",
        "zh": "<b>怎么用</b>:\n\n"
              "1) 点 <b>Menu → 搜索</b>\n"
              "2) 点大按钮 — 搜索\n"
              "3) <b>接受</b> → 视频通话\n\n"
              "交流语言在<b>聊天设置</b>里。\n"
              "帮助: /help",
        "ar": "<b>كيف يعمل</b>:\n\n"
              "1) اضغط <b>Menu → بحث</b>\n"
              "2) الزر الكبير — بحث\n"
              "3) <b>قبول</b> → مكالمة فيديو\n\n"
              "لغة التواصل في <b>إعدادات التواصل</b>.\n"
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
        "uz": "Buyruqlar:\n/help — qanday ishlaydi\n/start — boshiga\n/reset — profilni o‘chirish\n\nQidiruv: <b>Menu → Qidirish</b>\n\nFilm silkasini yuboring — nomini topib beraman (fayl emas).",
        "ru": "Команды:\n/help — как это работает\n/start — в начало\n/reset — удалить профиль\n\nПоиск: <b>Menu → Поиск</b>\n\nПришлите ссылку на фильм — скажу название (не файл).",
        "en": "Commands:\n/help — how it works\n/start — restart\n/reset — delete profile\n\nSearch: <b>Menu → Search</b>\n\nSend a movie link — I’ll find the title (not the file).",
        "de": "Befehle:\n/help — so geht’s\n/start — neu\n/reset — Profil löschen\n\nSuche: <b>Menu → Suche</b>\n\nFilm-Link senden — ich nenne den Titel (keine Datei).",
        "tg": "Фармонҳо:\n/help — чӣ гуна\n/start — аз аввал\n/reset — профил\n\nҶустуҷӯ: <b>Menu → Ҷустуҷӯ</b>\n\nПайванди филм фиристед — номро мегӯям (файл не).",
        "tr": "Komutlar:\n/help — nasıl çalışır\n/start — başa dön\n/reset — profil sil\n\nArama: <b>Menu → Ara</b>\n\nFilm linki gönderin — adını bulurum (dosya değil).",
        "ko": "명령:\n/help — 사용 방법\n/start — 처음으로\n/reset — 프로필 삭제\n\n검색: <b>Menu → 검색</b>\n\n영화 링크를 보내면 제목을 찾아드립니다 (파일 아님).",
        "ja": "コマンド:\n/help — 使い方\n/start — 最初から\n/reset — プロフィール削除\n\n検索: <b>Menu → 検索</b>\n\n映画リンクを送るとタイトルを調べます（ファイルは送りません）。",
        "zh": "命令：\n/help — 怎么用\n/start — 重新开始\n/reset — 删除资料\n\n搜索：<b>Menu → 搜索</b>\n\n发送电影链接 — 我会查找片名（不是文件）。",
        "ar": "الأوامر:\n/help — كيف يعمل\n/start — من البداية\n/reset — حذف الملف\n\nالبحث: <b>Menu → بحث</b>\n\nأرسل رابط فيلم — سأجد الاسم (وليس الملف).",
    },
    "link_looking": {
        "uz": "Silka tekshirilmoqda…",
        "ru": "Проверяю ссылку…",
        "en": "Checking the link…",
        "de": "Link wird geprüft…",
        "tg": "Пайванд санҷида мешавад…",
        "tr": "Bağlantı kontrol ediliyor…",
        "ko": "링크 확인 중…",
        "ja": "リンクを確認中…",
        "zh": "正在检查链接…",
        "ar": "جاري فحص الرابط…",
    },
    "link_found": {
        "uz": "🎬 Topilgan nom:\n<b>{title}</b>\n\nManba: {source}\n\n<i>Faqat nom — film fayli yuborilmaydi.</i>",
        "ru": "🎬 Найденное название:\n<b>{title}</b>\n\nИсточник: {source}\n\n<i>Только название — файл не отправляется.</i>",
        "en": "🎬 Found title:\n<b>{title}</b>\n\nSource: {source}\n\n<i>Title only — no file is sent.</i>",
        "de": "🎬 Gefundener Titel:\n<b>{title}</b>\n\nQuelle: {source}\n\n<i>Nur Titel — keine Datei.</i>",
        "tg": "🎬 Номи ёфтшуда:\n<b>{title}</b>\n\nМанба: {source}\n\n<i>Танҳо ном — файл фиристода намешавад.</i>",
        "tr": "🎬 Bulunan ad:\n<b>{title}</b>\n\nKaynak: {source}\n\n<i>Sadece ad — dosya gönderilmez.</i>",
        "ko": "🎬 찾은 제목:\n<b>{title}</b>\n\n출처: {source}\n\n<i>제목만 — 파일은 보내지 않습니다.</i>",
        "ja": "🎬 見つかったタイトル:\n<b>{title}</b>\n\n出典: {source}\n\n<i>タイトルのみ — ファイルは送りません。</i>",
        "zh": "🎬 找到的片名：\n<b>{title}</b>\n\n来源：{source}\n\n<i>仅片名 — 不发送文件。</i>",
        "ar": "🎬 الاسم الموجود:\n<b>{title}</b>\n\nالمصدر: {source}\n\n<i>الاسم فقط — لا يُرسل الملف.</i>",
    },
    "link_not_found": {
        "uz": "Bu silka orqali nomni o‘qib bo‘lmadi.\n\nOchiq post/sahifa silkasini yuboring (YouTube, TikTok, ochiq Instagram, IMDb). Yopiq yoki login talab qiladigan postlar ishlamasligi mumkin.\n\n<i>Faqat nom qidiriladi — film yuklanmaydi.</i>",
        "ru": "Не удалось прочитать название по ссылке.\n\nПришлите открытый пост/страницу (YouTube, TikTok, открытый Instagram, IMDb). Закрытые/login-ссылки могут не работать.\n\n<i>Ищем только название — фильм не скачивается.</i>",
        "en": "Couldn’t read a title from that link.\n\nTry a public post/page (YouTube, TikTok, public Instagram, IMDb). Private/login links may fail.\n\n<i>Title lookup only — no download.</i>",
        "de": "Titel aus dem Link nicht lesbar.\n\nÖffentlichen Post/Seite senden (YouTube, TikTok, öffentliches Instagram, IMDb).\n\n<i>Nur Titelsuche — kein Download.</i>",
        "tg": "Аз ин пайванд ном хонда нашуд.\n\nСаҳифаи кушода фиристед (YouTube/TikTok/Instagram/IMDb).\n\n<i>Танҳо ном — боргирӣ не.</i>",
        "tr": "Bu bağlantıdan ad okunamadı.\n\nAçık bir gönderi/sayfa gönderin (YouTube, TikTok, açık Instagram, IMDb).\n\n<i>Sadece ad — indirme yok.</i>",
        "ko": "그 링크에서 제목을 읽지 못했습니다.\n\n공개 게시물/페이지를 보내세요 (YouTube, TikTok, 공개 Instagram, IMDb).\n\n<i>제목만 — 다운로드 없음.</i>",
        "ja": "そのリンクからタイトルを読めませんでした。\n\n公開ポスト/ページを送ってください（YouTube、TikTok、公開Instagram、IMDb）。\n\n<i>タイトルのみ — ダウンロードなし。</i>",
        "zh": "无法从该链接读取片名。\n\n请发送公开帖子/页面（YouTube、TikTok、公开 Instagram、IMDb）。\n\n<i>仅查片名 — 不下载。</i>",
        "ar": "تعذر قراءة الاسم من هذا الرابط.\n\nأرسل منشوراً/صفحة عامة (YouTube وTikTok وInstagram العام وIMDb).\n\n<i>البحث عن الاسم فقط — بلا تنزيل.</i>",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    entry = TRANSLATIONS.get(key, {})
    template = entry.get(lang) or entry.get("en") or entry.get("uz") or key
    return template.format(**kwargs)


def gender_label(lang: str, gender: str) -> str:
    return t(lang, "gender_male" if gender == "male" else "gender_female")
