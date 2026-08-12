# Soyla — Telegram Mini App + LiveKit

Tasodifiy suhbatdosh topish: ro'yxat → matching → Mini App ichida **LiveKit audio/video qo'ng'iroq**.

## Imkoniyatlar

- Ro'yxatdan o'tish (aiogram FSM, 18+)
- Redis matching (yosh/jins/til/shahar) + ikki tomonlama rozilik
- PostgreSQL (user + CallSession + Block + Report + SavedPartner)
- Telegram Mini App (qidiruv, saqlanganlar, sozlamalar, qo'ng'iroq)
- LiveKit audio + video (mute/camera)
- Shikoyat / bloklash + admin buyruqlar (`ADMIN_IDS`)

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
   - `.env` da `DEV_TEST_MODE` bo'lsa **o'chiring** (endi kerak emas)

2. Docker:
   ```powershell
   git pull origin main
   docker compose up -d --force-recreate
   ```
   (To'liq `--build` ba'zan PyPI tarmoq xatosi beradi — kod volume orqali yangilanadi.)

3. Tashqi HTTPS (birini tanlang):
   - **ngrok:** `ngrok http 8000`
   - **Cloudflare Quick Tunnel (tekin):** batafsil → [deploy/TUNNEL.md](deploy/TUNNEL.md)
     ```powershell
     cloudflared tunnel --url http://localhost:8000
     ```
   `WEBAPP_URL=https://...` (oxirida `/webapp/` yo‘q)  
   BotFather Menu: `https://.../webapp/`

4. Tekshiruv:
   ```powershell
   curl.exe http://localhost:8000/health
   docker compose logs api --tail 30
   docker compose logs bot --tail 30
   ```
   `livekit_configured: true` va logda `Soyla API up` bo'lishi kerak.

5. Telegram: `/start` → Mini App → **Soyla** → Qidirish.

## 2 akkaunt bilan match test

1. Biri **erkak**, biri **ayol** (yoki Sozlamalarda Suhbatdosh = **Farqi yo'q**)
2. Til **bir xil**
3. Sozlamalar → Suhbatdosh yoshi → **18+ (hammasi)** → Saqlash
4. Ikkalasi Mini Appni ochib **Qidirish**
5. Taklif chiqsa → Roziman → LiveKit qo'ng'iroq

Agar topilmasa: ikkalasida ham qidiruvni To'xtatish → Sozlamalarni qayta saqlash → yana Qidirish.

## Moderatsiya

Qo'ng'iroqda: **Bloklash** / **Shikoyat** (sabab tanlanadi → avtomatik blok + qo'ng'iroq tugaydi).

Admin (faqat `ADMIN_IDS`):
- `/admin` — yordam
- `/reports` — ochiq shikoyatlar
- `/ban <user_id>` / `/unban <user_id>`
- `/report_done <id>` / `/report_dismiss <id>`

## LiveKit

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxx
LIVEKIT_API_SECRET=...
```

## Saqlanganlar

- Qo'ng'iroqda **Saqlash** → Mini App **Saqlangan** bo'limi
- Online suhbatdoshni **Chaqirish** → taklif Mini Appda

## Matching qoidalari

- Jins: sozlamalardagi **Suhbatdosh** (erkak / ayol / farqi yo'q)
- Yosh: sozlamalardagi **Suhbatdosh yoshi** oralig'i (ikki tomonlama) — default **18+**
- Til bir xil; shahar — `search_scope=city` bo'lsa mos shahar
- Ikki tomonlama rozilik (taklif 120 soniya)
- Bekor qilish / rad etish → ikkinchi tomon qayta qidiruvga
