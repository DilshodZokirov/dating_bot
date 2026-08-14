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
        "uz": "Buyruqlar:\n/help — qanday ishlaydi\n/start — boshiga\n/reset — profilni o‘chirish\n\nQidiruv: <b>Menu → Qidirish</b>\n\nFilm silkasini yuboring — kadr bo‘yicha internetdan nomini topaman (caption emas, fayl emas).",
        "ru": "Команды:\n/help — как это работает\n/start — в начало\n/reset — удалить профиль\n\nПоиск: <b>Menu → Поиск</b>\n\nПришлите ссылку на фильм — найду название в интернете по кадру (не подпись, не файл).",
        "en": "Commands:\n/help — how it works\n/start — restart\n/reset — delete profile\n\nSearch: <b>Menu → Search</b>\n\nSend a movie link — I’ll identify the title from the internet by the frame (not caption, not the file).",
        "de": "Befehle:\n/help — so geht’s\n/start — neu\n/reset — Profil löschen\n\nSuche: <b>Menu → Suche</b>\n\nFilm-Link senden — ich nenne den Titel (keine Datei).",
        "tg": "Фармонҳо:\n/help — чӣ гуна\n/start — аз аввал\n/reset — профил\n\nҶустуҷӯ: <b>Menu → Ҷустуҷӯ</b>\n\nПайванди филм фиристед — номро мегӯям (файл не).",
        "tr": "Komutlar:\n/help — nasıl çalışır\n/start — başa dön\n/reset — profil sil\n\nArama: <b>Menu → Ara</b>\n\nFilm linki gönderin — adını bulurum (dosya değil).",
        "ko": "명령:\n/help — 사용 방법\n/start — 처음으로\n/reset — 프로필 삭제\n\n검색: <b>Menu → 검색</b>\n\n영화 링크를 보내면 제목을 찾아드립니다 (파일 아님).",
        "ja": "コマンド:\n/help — 使い方\n/start — 最初から\n/reset — プロフィール削除\n\n検索: <b>Menu → 検索</b>\n\n映画リンクを送るとタイトルを調べます（ファイルは送りません）。",
        "zh": "命令：\n/help — 怎么用\n/start — 重新开始\n/reset — 删除资料\n\n搜索：<b>Menu → 搜索</b>\n\n发送电影链接 — 我会查找片名（不是文件）。",
        "ar": "الأوامر:\n/help — كيف يعمل\n/start — من البداية\n/reset — حذف الملف\n\nالبحث: <b>Menu → بحث</b>\n\nأرسل رابط فيلم — سأجد الاسم (وليس الملف).",
    },
    "link_looking": {
        "uz": "Silka kadri internetdan qidirilmoqda…",
        "ru": "Ищу фильм по кадру в интернете…",
        "en": "Searching the internet by the video frame…",
        "de": "Suche im Internet anhand des Videobilds…",
        "tg": "Интернет аз рӯи кадр ҷустуҷӯ…",
        "tr": "Kareye göre internette aranıyor…",
        "ko": "영상 프레임으로 인터넷 검색 중…",
        "ja": "映像フレームでインターネット検索中…",
        "zh": "正在按画面在互联网搜索…",
        "ar": "جاري البحث في الإنترنت حسب الإطار…",
    },
    "link_found": {
        "uz": "🎬 Topilgan film:\n<b>{title}</b>\n\nManba: {source}\n\n<i>Internetdan aniqlangan nom — film fayli yuborilmaydi.</i>",
        "ru": "🎬 Найденный фильм:\n<b>{title}</b>\n\nИсточник: {source}\n\n<i>Название из интернета — файл не отправляется.</i>",
        "en": "🎬 Identified movie:\n<b>{title}</b>\n\nSource: {source}\n\n<i>Title from internet lookup — no file is sent.</i>",
        "de": "🎬 Gefundener Film:\n<b>{title}</b>\n\nQuelle: {source}\n\n<i>Titel aus Internetsuche — keine Datei.</i>",
        "tg": "🎬 Филми ёфтшуда:\n<b>{title}</b>\n\nМанба: {source}\n\n<i>Аз интернет — файл не.</i>",
        "tr": "🎬 Bulunan film:\n<b>{title}</b>\n\nKaynak: {source}\n\n<i>İnternetten — dosya yok.</i>",
        "ko": "🎬 찾은 영화:\n<b>{title}</b>\n\n출처: {source}\n\n<i>인터넷 조회 — 파일 없음.</i>",
        "ja": "🎬 特定した映画:\n<b>{title}</b>\n\n出典: {source}\n\n<i>インターネット特定 — ファイルなし。</i>",
        "zh": "🎬 识别到的电影：\n<b>{title}</b>\n\n来源：{source}\n\n<i>来自互联网识别 — 不发送文件。</i>",
        "ar": "🎬 الفيلم المعرف:\n<b>{title}</b>\n\nالمصدر: {source}\n\n<i>من الإنترنت — بلا ملف.</i>",
    },
    "link_not_found": {
        "uz": "Bu silka bo‘yicha internetdan film nomini aniqlab bo‘lmadi.\n\nSabablar: yopiq Instagram/TikTok, preview rasm yo‘q, yoki kadr bazada topilmadi.\nOchilgan post yoki YouTube/IMDb silkasini qayta yuboring.\n\n<i>Faqat nom — film yuklanmaydi.</i>",
        "ru": "Не удалось определить название фильма в интернете по этой ссылке.\n\nВозможные причины: закрытый Instagram/TikTok, нет превью, кадр не найден.\nПопробуйте открытый пост или YouTube/IMDb.\n\n<i>Только название — фильм не скачивается.</i>",
        "en": "Couldn’t identify the movie on the internet from that link.\n\nPossible reasons: private Instagram/TikTok, no preview image, or frame not found.\nTry a public post or YouTube/IMDb.\n\n<i>Title only — no download.</i>",
        "de": "Filmtitel im Internet nicht erkannt.\n\nPrivat/kein Vorschaubild/kein Treffer. Öffentlichen Post oder YouTube/IMDb versuchen.\n\n<i>Nur Titel — kein Download.</i>",
        "tg": "Аз интернет ном муайян нашуд.\n\nПости кушода ё YouTube/IMDb.\n\n<i>Танҳо ном.</i>",
        "tr": "İnternetten film adı belirlenemedi.\n\nAçık gönderi veya YouTube/IMDb deneyin.\n\n<i>Sadece ad.</i>",
        "ko": "인터넷에서 영화 제목을 찾지 못했습니다.\n\n공개 게시물 또는 YouTube/IMDb를 시도하세요.\n\n<i>제목만.</i>",
        "ja": "インターネットで映画を特定できませんでした。\n\n公開ポストか YouTube/IMDb を試してください。\n\n<i>タイトルのみ。</i>",
        "zh": "无法从互联网识别该链接的电影名。\n\n请尝试公开帖子或 YouTube/IMDb。\n\n<i>仅片名。</i>",
        "ar": "تعذر التعرف على اسم الفيلم عبر الإنترنت.\n\nجرّب منشوراً عاماً أو YouTube/IMDb.\n\n<i>الاسم فقط.</i>",
    },
    "link_need_gemini": {
        "uz": "Instagram/TikTok kadrini aniqlash uchun <b>GEMINI_API_KEY</b> kerak.\n\n1) https://aistudio.google.com/apikey dan bepul kalit oling\n2) .env fayliga qo‘shing:\n<code>GEMINI_API_KEY=...</code>\n3) <code>docker compose up -d --force-recreate</code>\n\nKeyin shu silkani qayta yuboring.\n\n<i>Faqat nom — film yuklanmaydi.</i>",
        "ru": "Чтобы распознать кадр Instagram/TikTok нужен <b>GEMINI_API_KEY</b>.\n\n1) Бесплатный ключ: https://aistudio.google.com/apikey\n2) В .env:\n<code>GEMINI_API_KEY=...</code>\n3) <code>docker compose up -d --force-recreate</code>\n\n<i>Только название.</i>",
        "en": "To identify Instagram/TikTok frames you need <b>GEMINI_API_KEY</b>.\n\n1) Free key: https://aistudio.google.com/apikey\n2) Add to .env:\n<code>GEMINI_API_KEY=...</code>\n3) <code>docker compose up -d --force-recreate</code>\n\n<i>Title only.</i>",
        "de": "Für Instagram/TikTok-Frames wird <b>GEMINI_API_KEY</b> benötigt.\n\nhttps://aistudio.google.com/apikey → .env → recreate.",
        "tg": "Instagram/TikTok барои <b>GEMINI_API_KEY</b> лозим аст.\n\nhttps://aistudio.google.com/apikey",
        "tr": "Instagram/TikTok için <b>GEMINI_API_KEY</b> gerekli.\n\nhttps://aistudio.google.com/apikey",
        "ko": "Instagram/TikTok 인식에는 <b>GEMINI_API_KEY</b>가 필요합니다.\n\nhttps://aistudio.google.com/apikey",
        "ja": "Instagram/TikTok の特定には <b>GEMINI_API_KEY</b> が必要です。\n\nhttps://aistudio.google.com/apikey",
        "zh": "识别 Instagram/TikTok 需要 <b>GEMINI_API_KEY</b>。\n\nhttps://aistudio.google.com/apikey",
        "ar": "للتعرّف على Instagram/TikTok يلزم <b>GEMINI_API_KEY</b>.\n\nhttps://aistudio.google.com/apikey",
    },
    "link_need_preview": {
        "uz": "Bu silkadаn preview rasm olinmadi (yopiq post yoki Instagram blokladi).\n\nOchilgan post silkasini yuboring yoki ekran kadrasini rasm qilib yuboring (keyingi yangilanish).\n\n<i>Faqat nom.</i>",
        "ru": "Не удалось получить превью по ссылке (закрытый пост).\n\nПришлите открытый пост.\n\n<i>Только название.</i>",
        "en": "Couldn’t get a preview image from that link (private/blocked).\n\nSend a public post link.\n\n<i>Title only.</i>",
        "de": "Kein Vorschaubild. Öffentlichen Post senden.",
        "tg": "Превю нест. Пости кушода фиристед.",
        "tr": "Önizleme yok. Açık gönderi gönderin.",
        "ko": "미리보기 없음. 공개 게시물을 보내세요.",
        "ja": "プレビューなし。公開ポストを送ってください。",
        "zh": "无法获取预览。请发送公开帖子。",
        "ar": "لا توجد معاينة. أرسل منشوراً عاماً.",
    },
    "link_guide": {
        "uz": "<b>🎬 Film nomini silka orqali topish</b>\n\n"
              "<b>Qanday:</b>\n"
              "1) Instagram/TikTok/YouTube silkasini botga yuboring\n"
              "2) Bot postdagi <b>kadr/preview</b> ni oladi\n"
              "3) Shu rasm bo‘yicha <b>internetdan</b> filmni qidiradi\n"
              "4) Topilsa haqiqiy nom chiqadi\n\n"
              "<b>Muhim:</b> post caption/tavsifi o‘qilmaydi — internet qidiruv.\n"
              "Yopiq postlar yoki rasm chiqmasa ishlamasligi mumkin.\n\n"
              "<i>Faqat nom — film fayli yuborilmaydi.</i>",
        "ru": "<b>🎬 Название фильма по ссылке</b>\n\n"
              "1) Пришлите ссылку Instagram/TikTok/YouTube\n"
              "2) Бот берёт <b>кадр/превью</b>\n"
              "3) Ищет фильм <b>в интернете</b> по изображению\n"
              "4) Показывает настоящее название\n\n"
              "<b>Важно:</b> подпись поста не используется.\n\n"
              "<i>Только название — файл не отправляется.</i>",
        "en": "<b>🎬 Find a movie title from a link</b>\n\n"
              "1) Send an Instagram/TikTok/YouTube link\n"
              "2) Bot takes the <b>preview frame</b>\n"
              "3) Searches the <b>internet</b> by that image\n"
              "4) Returns the real movie title\n\n"
              "<b>Important:</b> post captions are not used as the answer.\n\n"
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
