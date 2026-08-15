from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.api.signaling import router as signaling_router
from app.api.webapp import router as webapp_api_router
from app.config import settings
from app.database import init_db
from app.livekit_tokens import livekit_configured
import app.models  # noqa: F401 — create_all uchun jadvallar


class NoCacheStaticFiles(StaticFiles):
    """Mini App HTML/JS keshini Telegram WebView da yangilash osonroq bo‘lsin."""

    async def get_response(self, path: str, scope):
        response: Response = await super().get_response(path, scope)
        if path.endswith(".html") or path in ("", "/", "index.html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response


app = FastAPI(title="Soyla API")

app.include_router(webapp_api_router)
app.include_router(signaling_router)
app.mount("/webapp", NoCacheStaticFiles(directory="app/webapp", html=True), name="webapp")


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
