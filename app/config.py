from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    database_url: str
    redis_url: str

    min_age: int = 18
    max_age_gap: int = 5  # matching qilinadigan foydalanuvchilar orasidagi maksimal yosh farqi

    webapp_url: str = ""  # Mini App uchun ochiq HTTPS manzil (masalan ngrok / Render)

    # Dev test mode — bitta Telegram akkaunt bilan match/call tekshirish
    # PRODUCTIONDA hech qachon true qilmang!
    dev_test_mode: bool = False
    # Ixtiyoriy; bo'sh bo'lsa bot_token dan hosil qilinadi
    dev_test_secret: str = ""

    # LiveKit (audio/video qo'ng'iroq) — Bgalaxy dagi kabi
    livekit_url: str = ""  # wss://xxx.livekit.cloud
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # TURN (ixtiyoriy; LiveKit bo'lsa odatda kerak emas)
    metered_domain: str = ""
    metered_secret_key: str = ""
    turn_urls: str = ""
    turn_username: str = ""
    turn_password: str = ""

    # Admin Telegram ID lar (vergul bilan): 123,456
    admin_ids: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("dev_test_mode", mode="before")
    @classmethod
    def _parse_dev_test_mode(cls, v):
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        return str(v).strip().lower() in {"1", "true", "yes", "on", "y"}

    def admin_id_set(self) -> set[int]:
        ids: set[int] = set()
        for part in (self.admin_ids or "").split(","):
            part = part.strip()
            if part.isdigit():
                ids.add(int(part))
        return ids


settings = Settings()
