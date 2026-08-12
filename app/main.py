from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.signaling import router as signaling_router
from app.api.webapp import router as webapp_api_router
from app.config import settings
from app.database import init_db
from app.livekit_tokens import livekit_configured
import app.models  # noqa: F401 — create_all uchun jadvallar

app = FastAPI(title="Soyla API")

app.include_router(webapp_api_router)
app.include_router(signaling_router)
app.mount("/webapp", StaticFiles(directory="app/webapp", html=True), name="webapp")


@app.on_event("startup")
async def on_startup():
    await init_db()
    print(
        f"Soyla API up | webapp_url={'set' if settings.webapp_url else 'EMPTY'} "
        f"| livekit={'ok' if livekit_configured() else 'MISSING'}",
        flush=True,
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "webapp_url_set": bool(settings.webapp_url),
        "livekit_configured": livekit_configured(),
    }
