from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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
    print(f"DEV_TEST_MODE={settings.dev_test_mode}", flush=True)


@app.get("/health")
async def health():
    return {"status": "ok", "dev_test_mode": settings.dev_test_mode}
