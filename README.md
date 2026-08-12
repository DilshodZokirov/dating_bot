# Dating Bot — Telegram + FastAPI + LiveKit

Tasodifiy suhbatdosh topish: ro'yxat → matching → Mini App ichida **LiveKit audio/video qo'ng'iroq**.

## Imkoniyatlar

- ✅ Ro'yxatdan o'tish (aiogram FSM, 18+)
- ✅ Redis matching (yosh/jins/til/shahar) + ikki tomonlama rozilik
- ✅ PostgreSQL (user + CallSession + Block + Report)
- ✅ Telegram Mini App (qidiruv, profil, qo'ng'iroq)
- ✅ **LiveKit** audio + video (mute/camera)
- ✅ Dev test mode (1 Telegram akkaunt + kompyuter)
- ✅ **Shikoyat / bloklash** + admin buyruqlar (`ADMIN_IDS`)

## Ishga tushirish

1. `.env` yarating:
   ```bash
   cp .env.example .env
   ```
   To'ldiring:
   - `BOT_TOKEN`
   - `WEBAPP_URL` (HTTPS, ngrok) — **oxirida `/webapp/` yo'q**
   - `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET`
   - `ADMIN_IDS` — o'zingizning Telegram ID (vergul bilan bir nechta)
   - test uchun `DEV_TEST_MODE=true`

2. Docker:
   ```bash
   docker compose up -d --force-recreate
   ```
   (To'liq `--build` ba'zan PyPI tarmoq xatosi beradi — kod volume orqali yangilanadi.)

3. Telegram: `/start` → Mini App → Qidirish yoki **Test match**.

## Moderatsiya

Qo'ng'iroqda: **Bloklash** / **Shikoyat** (sabab tanlanadi → avtomatik blok + qo'ng'iroq tugaydi).

Admin (faqat `ADMIN_IDS`):
- `/admin` — yordam
- `/reports` — ochiq shikoyatlar
- `/ban <user_id>` / `/unban <user_id>`
- `/report_done <id>` / `/report_dismiss <id>`

Shikoyat kelganda adminlarga Telegram xabar ketadi.

## LiveKit

Bgalaxy/Zoom tipidagi SFU. Alohida TURN sozlash shart emas — LiveKit Cloud o'zi hal qiladi.

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxx
LIVEKIT_API_SECRET=...
```

## Dev test mode

1. `DEV_TEST_MODE=true`
2. Mini App → **Test match**
3. Havolani kompyuterda oching → **Start**

## Keyingi qadamlar

- Yosh tasdiqlash
- Admin web panel

## Saqlanganlar va xabarlar

- Qo'ng'iroqda **Saqlash** → Mini App **Saqlangan** bo'limi
- Mos suhbatdosh topilganda Telegramda **inline** xabar + Mini App tugmasi
- Saqlangan online suhbatdoshni **Chaqirish** → taklif + xabar (ikkala tomon qabul qiladi)

## Matching qoidalari

- Jins: sozlamalardagi **Suhbatdosh** (erkak / ayol / farqi yo'q)
- Yosh: sozlamalardagi **Suhbatdosh yoshi** oralig'i (ikki tomonlama)
- Til bir xil; shahar — `search_scope=city` bo'lsa mos shahar
- Ikki tomonlama rozilik (taklif 120 soniya)
- Bekor qilish / rad etish → ikkinchi tomon qayta qidiruvga
- Foydalanuvchiga "navbat" ko'rsatilmaydi — faqat qidiruv holati
