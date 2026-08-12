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

    # TURN (WebRTC) — mobil tarmoqda audio/video uchun muhim
    metered_domain: str = ""  # masalan: xxx.metered.live
    metered_secret_key: str = ""
    # Ixtiyoriy o'z TURN (masalan docker coturn): turn:host:3478?transport=udp
    turn_urls: str = ""
    turn_username: str = ""
    turn_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
