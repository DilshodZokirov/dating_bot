from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Mavjud DB ga yangi ustunlar (create_all qo'shmaydi)
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS prefer_age_min INTEGER DEFAULT 12")
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS prefer_age_max INTEGER DEFAULT 100")
        )
        await conn.execute(
            text("UPDATE users SET prefer_age_min = 12 WHERE prefer_age_min IS NULL")
        )
        await conn.execute(
            text("UPDATE users SET prefer_age_max = 100 WHERE prefer_age_max IS NULL")
        )
        # Eski fixed bracket / 18–99 default → keng 12–100 (foydalanuvchi keyin o'zi toraytiradi)
        await conn.execute(
            text(
                """
                UPDATE users SET prefer_age_min = 12, prefer_age_max = 100
                WHERE (prefer_age_min, prefer_age_max) IN (
                    (18, 99), (18, 19), (20, 24), (25, 29), (30, 34),
                    (35, 39), (40, 49), (50, 59), (60, 99)
                )
                """
            )
        )
        # Tiqilib qolgan qo'ng'iroq holati
        await conn.execute(text("UPDATE users SET is_in_call = false WHERE is_in_call = true"))
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS has_avatar BOOLEAN DEFAULT false")
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS match_topic VARCHAR(32) DEFAULT 'any'")
        )
        await conn.execute(
            text("UPDATE users SET match_topic = 'any' WHERE match_topic IS NULL OR match_topic = ''")
        )
        # Speaking mavzular olib tashlandi — til Language ustunida
        await conn.execute(
            text("UPDATE users SET match_topic = 'any' WHERE match_topic LIKE 'speak_%'")
        )
        # Yangi tillar (PostgreSQL enum `language`)
        for lang in ("de", "tg", "tr", "ko", "ja", "zh", "ar"):
            try:
                async with conn.begin_nested():
                    await conn.execute(
                        text(f"ALTER TYPE language ADD VALUE IF NOT EXISTS '{lang}'")
                    )
            except Exception:
                pass
        # Dastur tili (UI) — matching tilidan alohida
        try:
            async with conn.begin_nested():
                await conn.execute(
                    text("ALTER TABLE users ADD COLUMN IF NOT EXISTS ui_language language")
                )
        except Exception:
            try:
                async with conn.begin_nested():
                    await conn.execute(
                        text(
                            "ALTER TABLE users ADD COLUMN IF NOT EXISTS ui_language VARCHAR(16) DEFAULT 'uz'"
                        )
                    )
            except Exception:
                pass
        await conn.execute(
            text(
                """
                UPDATE users
                SET ui_language = language
                WHERE ui_language IS NULL
                """
            )
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(32)")
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS ban_until TIMESTAMPTZ")
        )
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS block_strike_count INTEGER DEFAULT 0"
            )
        )
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS report_strike_count INTEGER DEFAULT 0"
            )
        )
        await conn.execute(
            text("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS read_at TIMESTAMPTZ")
        )
        await conn.execute(
            text(
                """
                UPDATE users
                SET block_strike_count = 0
                WHERE block_strike_count IS NULL
                """
            )
        )
        await conn.execute(
            text(
                """
                UPDATE users
                SET report_strike_count = 0
                WHERE report_strike_count IS NULL
                """
            )
        )
