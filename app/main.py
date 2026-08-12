from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.api.signaling import router as signaling_router
from app.api.webapp import router as webapp_api_router
from app.config import settings
from app.database import init_db
import app.models  # noqa: F401 — create_all uchun jadvallar

app = FastAPI(title="Dating Bot API")

app.include_router(webapp_api_router)
app.include_router(signaling_router)
app.mount("/webapp", StaticFiles(directory="app/webapp", html=True), name="webapp")


@app.on_event("startup")
async def on_startup():
    await init_db()
    raw = os.environ.get("DEV_TEST_MODE", "<unset>")
    print(f"DEV_TEST_MODE raw={raw!r} parsed={settings.dev_test_mode}", flush=True)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "dev_test_mode": settings.dev_test_mode,
        "dev_test_mode_raw": os.environ.get("DEV_TEST_MODE"),
    }
