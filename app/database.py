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
