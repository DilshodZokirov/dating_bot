# Soyla — Production deploy (VPS)

Ngrok o‘rniga **doimiy domen + HTTPS**. LiveKit Cloud o‘zgarishsiz qoladi.

## Kerak

1. **VPS** (Ubuntu 22.04+): 1 vCPU / 1–2 GB RAM yetadi  
   (Hetzner, DigitalOcean, Timeweb, …)
2. **Domen** (masalan `app.soyla.uz` yoki `soyla-bot.example.com`)
3. DNS da **A-record** → VPS IP (proxied emas yoki Cloudflare SSL Full)

## 1. VPS ga ulanish

```bash
ssh root@YOUR_VPS_IP
apt update && apt install -y git curl
```

Docker o‘rnatish:

```bash
curl -fsSL https://get.docker.com | sh
```

## 2. Loyihani clone

```bash
git clone https://github.com/DilshodZokirov/dating_bot.git
cd dating_bot
cp .env.example .env
nano .env
```

`.env` misol:

```env
BOT_TOKEN=...
DOMAIN=app.soyla.uz
WEBAPP_URL=https://app.soyla.uz

POSTGRES_USER=postgres
POSTGRES_PASSWORD=kuchli-parol
POSTGRES_DB=dating_bot
DATABASE_URL=postgresql+asyncpg://postgres:kuchli-parol@db:5432/dating_bot
REDIS_URL=redis://redis:6379/0

MIN_AGE=18
MAX_AGE_GAP=5

LIVEKIT_URL=wss://xxx.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...

ADMIN_IDS=sizning_telegram_id
```

Muhim:
- `WEBAPP_URL` = `https://DOMAIN` — **oxirida `/webapp/` yo‘q**
- `DOMAIN` = Caddy uchun (Let's Encrypt)
- `DEV_TEST_MODE` yo‘q

## 3. Ishga tushirish

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f api
```

Tekshiruv:

```bash
curl https://app.soyla.uz/health
```

`livekit_configured: true` bo‘lishi kerak.

## 4. BotFather

Menu Button URL:

```
https://app.soyla.uz/webapp/
```

Botda `/start` → Mini App ochiladi.

## 5. Yangilash

```bash
cd ~/dating_bot
bash deploy/update.sh
```

yoki:

```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

## Firewall

```bash
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

Postgres/Redis tashqariga ochilmaydi (faqat Docker ichida).

## Muammolar

| Belgi | Yechim |
|--------|--------|
| Caddy sertifikat olmaydi | DNS A-record VPS IP ga qaraganini tekshiring; 80/443 ochiq |
| Mini App ochilmaydi | BotFather URL + `WEBAPP_URL` bir xil domen |
| Empty reply / API o‘lik | `docker compose -f docker-compose.prod.yml logs api` |
| Match yo‘q | 2 akkaunt: jins/til/yosh 18+ (README test) |

## Lokal vs Production

| | Lokal | Production |
|--|--------|------------|
| Compose | `docker-compose.yml` | `docker-compose.prod.yml` |
| HTTPS | ngrok | Caddy + domen |
| DB port | 5432 ochiq | yopiq |
| Kod | volume mount | image build |
