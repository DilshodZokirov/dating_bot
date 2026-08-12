# Dating Bot — Telegram + FastAPI + LiveKit

Tasodifiy suhbatdosh topish: ro'yxat → matching → Mini App ichida **LiveKit audio/video qo'ng'iroq**.

## Imkoniyatlar

- ✅ Ro'yxatdan o'tish (aiogram FSM, 18+)
- ✅ Redis matching (yosh/jins/til/shahar) + ikki tomonlama rozilik
- ✅ PostgreSQL (user + CallSession)
- ✅ Telegram Mini App (qidiruv, profil, qo'ng'iroq)
- ✅ **LiveKit** audio + video (mute/camera)
- ✅ Dev test mode (1 Telegram akkaunt + kompyuter)

## Ishga tushirish

1. `.env` yarating:
   ```bash
   cp .env.example .env
   ```
   To'ldiring:
   - `BOT_TOKEN`
   - `WEBAPP_URL` (HTTPS, ngrok)
   - `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET`
   - test uchun `DEV_TEST_MODE=true`

2. Docker:
   ```bash
   docker compose up --build
   ```

3. Telegram: `/start` → Mini App → Qidirish yoki **Test match**.

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

- Shikoyat / bloklash
- Admin panel
- Yosh tasdiqlash
