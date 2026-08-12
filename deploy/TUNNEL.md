# Cloudflare Tunnel — kompyuter = server (tekin)

Ngrok o‘rniga. Docker (`api` :8000) lokalda ishlaydi, tashqariga Cloudflare orqali ochiladi.

## Variant A — Quick Tunnel (eng oson, akkaunt shart emas)

URL har safar yangi bo‘ladi (`*.trycloudflare.com`) — ngrok kabi. Lekin tekin.

### 1. Docker ishlasin
```powershell
docker compose up -d --force-recreate
curl.exe http://localhost:8000/health
```

### 2. cloudflared o‘rnating (Windows)

1. https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. `cloudflared-windows-amd64.exe` yuklab oling
3. Masalan `C:\cloudflared\cloudflared.exe` ga qo‘ying

Yoki winget:
```powershell
winget install --id Cloudflare.cloudflared
```

### 3. Tunnel oching
```powershell
cloudflared tunnel --url http://localhost:8000
```

Chiqadi:
```
https://random-words.trycloudflare.com
```

### 4. `.env` va BotFather
```env
WEBAPP_URL=https://random-words.trycloudflare.com
```
BotFather Menu: `https://random-words.trycloudflare.com/webapp/`

```powershell
docker compose up -d --force-recreate
```

**Eslatma:** `cloudflared` oynasini yopmang. Kompyuter sleep qilmasin.

---

## Variant B — Named Tunnel (doimiy URL, domen kerak)

Agar tekin/arzon domeningiz bo‘lsa va u Cloudflare DNS da bo‘lsa — URL **o‘zgarmaydi**.

1. [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) → **Networks** → **Tunnels** → Create
2. Connector: Cloudflared → token nusxa
3. Public hostname: `app.sizning.domen` → `http://api:8000` (Docker ichida) yoki `http://host.docker.internal:8000`

Docker Compose (token bilan):

```powershell
# .env ga qo'shing:
# CLOUDFLARE_TUNNEL_TOKEN=eyJ...
docker compose --profile tunnel up -d
```

`.env`:
```env
DOMAIN=app.sizning.domen
WEBAPP_URL=https://app.sizning.domen
CLOUDFLARE_TUNNEL_TOKEN=eyJ...
```

BotFather: `https://app.sizning.domen/webapp/`

---

## Qiyoslash

| | Ngrok free | CF Quick | CF Named |
|--|------------|----------|----------|
| Akkaunt | ixtiyoriy | shart emas | kerak |
| Domen | yo‘q | yo‘q | kerak |
| URL o‘zgaradi | ha | ha | **yo‘q** |
| Tekin | ha | ha | ha (tunnel) |

**Hozir tavsiya:** Variant A (Quick Tunnel).  
Domen olsangiz → Variant B.
