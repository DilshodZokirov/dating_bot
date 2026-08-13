from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    database_url: str
    redis_url: str

    min_age: int = 12  # o'z yoshi minimal (12+)
    max_age_gap: int = 5  # ishlatilmaydi — oraliqni foydalanuvchi o'zi tanlaydi

    webapp_url: str = ""  # Mini App uchun ochiq HTTPS manzil (masalan ngrok / Render)

    # LiveKit (audio/video qo'ng'iroq)
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

    def admin_id_set(self) -> set[int]:
        ids: set[int] = set()
        for part in (self.admin_ids or "").split(","):
            part = part.strip()
            if part.isdigit():
                ids.add(int(part))
        return ids


settings = Settings()
