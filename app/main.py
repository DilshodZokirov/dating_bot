from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.signaling import router as signaling_router
from app.api.webapp import router as webapp_api_router
from app.database import init_db

app = FastAPI(title="Dating Bot API")

app.include_router(webapp_api_router)
app.include_router(signaling_router)
app.mount("/webapp", StaticFiles(directory="app/webapp", html=True), name="webapp")


@app.on_event("startup")
async def on_startup():
    from app.config import settings
    from app import test_mode

    print(
        f"API startup: DEV_TEST_MODE={settings.dev_test_mode} "
        f"enabled={test_mode.is_enabled()} WEBAPP_URL={settings.webapp_url!r}",
        flush=True,
    )
    await init_db()


@app.get("/health")
async def health():
    from app import test_mode

    return {"status": "ok", "test_mode": test_mode.is_enabled()}
