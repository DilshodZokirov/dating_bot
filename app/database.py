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


async def _ensure_user_pref_columns(conn) -> None:
    """Eski DB ga prefer_age_* ustunlarini qo'shadi. Xato bo'lsa API ni o'chirmaydi."""
    statements = [
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS prefer_age_min INTEGER DEFAULT 18",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS prefer_age_max INTEGER DEFAULT 99",
        "UPDATE users SET prefer_age_min = 18 WHERE prefer_age_min IS NULL",
        "UPDATE users SET prefer_age_max = 99 WHERE prefer_age_max IS NULL",
    ]
    for sql in statements:
        try:
            await conn.execute(text(sql))
        except Exception as e:
            print(f"DB migrate skip: {sql[:48]}... -> {e}", flush=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_user_pref_columns(conn)
