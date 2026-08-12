# Dating Bot — Telegram + FastAPI + WebRTC

Tasodifiy suhbatdosh topish: ro'yxat → matching → Mini App ichida **audio/video qo'ng'iroq**.

## Imkoniyatlar

- ✅ Ro'yxatdan o'tish (aiogram FSM, 18+)
- ✅ Redis matching (yosh/jins/til/shahar) + ikki tomonlama rozilik
- ✅ PostgreSQL (user + CallSession)
- ✅ Telegram Mini App (qidiruv, profil, qo'ng'iroq)
- ✅ WebRTC P2P audio + video (mute/video toggle, perfect negotiation)
- ✅ TURN credential API (Metered yoki static TURN)

## Ishga tushirish

1. `.env` yarating:
   ```bash
   cp .env.example .env
   ```
   `BOT_TOKEN` va `WEBAPP_URL` (HTTPS, masalan ngrok / cloud) ni to'ldiring.

2. Docker:
   ```bash
   docker compose up --build
   ```

3. Telegram botda `/start` → Mini App tugmasi → Qidirish.

## Video qo'ng'iroq ishlashi uchun

1. **WEBAPP_URL** — ochiq HTTPS (Telegram Mini App talabi).
2. **TURN** (mobil tarmoqda shart):
   - Metered: `METERED_DOMAIN` + `METERED_SECRET_KEY`
   - Yoki static: `TURN_URLS` + `TURN_USERNAME` + `TURN_PASSWORD`
3. Ikkalasi ham Mini App ochiq bo'lsin, mikrofon/kamera ruxsati berilsin.

## Keyingi qadamlar

- Shikoyat / bloklash
- Admin panel
- Yosh tasdiqlash

## Dev test mode (1 Telegram akkaunt)

Ikkinchi raqam bo‘lmasa, match + WebRTC ni shunday tekshirasiz:

1. `.env` da:
   ```bash
   DEV_TEST_MODE=true
   ```
2. `docker compose up --build`
3. Telefonda Mini App → **🧪 Test match**
4. Chiqqan havolani **kompyuter brauzerida** oching → **Start**
5. Telefon + kompyuter bir-biriga audio/video ulanishi kerak

**Muhim:** productionda `DEV_TEST_MODE=false` qoldiring.
