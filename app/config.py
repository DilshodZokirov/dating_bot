from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str

    database_url: str
    redis_url: str

    min_age: int = 18
    max_age_gap: int = 5  # matching qilinadigan foydalanuvchilar orasidagi maksimal yosh farqi

    webapp_url: str = ""  # Mini App uchun ochiq HTTPS manzil (masalan ngrok)

    metered_domain: str = ""  # masalan: soylaibot.metered.live
    metered_secret_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
