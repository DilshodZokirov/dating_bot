# Dating Bot — Telegram + FastAPI

Tasodifiy suhbatdosh topish boti: foydalanuvchilar ro'yxatdan o'tadi (ism, yosh, jins,
qidirayotgan jins), so'ng `/search` orqali navbatga qo'shiladi va mos kishi topilganda
ikkalasi bir-biriga ulanadi.

## Hozirgi holat (skeleton)

- ✅ Ro'yxatdan o'tish (aiogram FSM)
- ✅ Redis asosidagi matching navbati (yosh oralig'i va jins bo'yicha)
- ✅ PostgreSQL orqali foydalanuvchi va sessiya saqlash
- ⏳ **Audio/video qo'ng'iroq hali ulanmagan** — hozircha faqat "xona ID" generatsiya
  qilinadi. Buni real qo'ng'iroqqa aylantirish uchun WebRTC provayder (masalan LiveKit,
  Agora yoki Daily.co) bilan integratsiya va Telegram Mini App (Web App) frontend kerak
  bo'ladi. Bu keyingi bosqich.

## Ishga tushirish

1. `.env.example` faylini `.env` deb nusxalang va `BOT_TOKEN` hamda parollarni to'ldiring:
   ```bash
   cp .env.example .env
   ```

2. Docker orqali barcha servislarni ishga tushiring:
   ```bash
   docker compose up --build
   ```

   Bu quyidagilarni ishga tushiradi:
   - `db` — PostgreSQL
   - `redis` — Redis (matching navbati va FSM holatlari uchun)
   - `api` — FastAPI (hozircha faqat `/health` endpoint bor)
   - `bot` — Telegram bot (polling rejimida)

3. Botga Telegram’da `/start` yuboring.

## Muhim: xavfsizlik bo'yicha eslatma

- `MIN_AGE` sozlamasi orqali botdan faqat voyaga yetganlar (standart: 18 yosh)
  foydalanishi ta'minlangan. Buni pasaytirish tavsiya etilmaydi.
- Hozirgi `is_verified` maydoni hali ishlatilmayapti — real loyihada yoshni faqat
  o'z so'zi bilan emas, biror tasdiqlash mexanizmi (masalan hujjat yoki
  telefon raqami orqali) bilan tekshirish tavsiya etiladi.
- Foydalanuvchilarni bloklash (`is_banned`) va shikoyat qilish funksiyasini
  qo'shish kerak bo'ladi — bu hali qo'shilmagan.

## Keyingi qadamlar

- WebRTC/Mini App integratsiyasi (real audio/video qo'ng'iroq)
- Shikoyat va bloklash tizimi
- Admin panel (banned foydalanuvchilar, statistikalar)
- Yoshni tasdiqlash bosqichi
