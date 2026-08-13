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
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS prefer_age_min INTEGER DEFAULT 18")
        )
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS prefer_age_max INTEGER DEFAULT 99")
        )
        await conn.execute(
            text("UPDATE users SET prefer_age_min = 18 WHERE prefer_age_min IS NULL")
        )
        await conn.execute(
            text("UPDATE users SET prefer_age_max = 99 WHERE prefer_age_max IS NULL")
        )
        # Eski default (faqat o'z yosh bracketi) matchingni bloklagan — 18+ ga ochamiz
        await conn.execute(
            text(
                """
                UPDATE users SET prefer_age_min = 18, prefer_age_max = 99
                WHERE (prefer_age_min, prefer_age_max) IN (
                    (18, 19), (20, 24), (25, 29), (30, 34),
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
        for lang in ("de", "tg", "tr", "ko", "ja", "zh"):
            try:
                async with conn.begin_nested():
                    await conn.execute(
                        text(f"ALTER TYPE language ADD VALUE IF NOT EXISTS '{lang}'")
                    )
            except Exception:
                pass
