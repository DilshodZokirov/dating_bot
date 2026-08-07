from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    database_url: str
    redis_url: str

    min_age: int = 18
    max_age_gap: int = 5  # matching qilinadigan foydalanuvchilar orasidagi maksimal yosh farqi

    webapp_url: str = ""  # Mini App uchun ochiq HTTPS manzil (masalan ngrok / Render)

    # TURN (WebRTC) — mobil tarmoqda audio/video uchun muhim
    metered_domain: str = ""  # masalan: xxx.metered.live
    metered_secret_key: str = ""
    # Ixtiyoriy o'z TURN (masalan docker coturn): turn:host:3478?transport=udp
    turn_urls: str = ""
    turn_username: str = ""
    turn_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
