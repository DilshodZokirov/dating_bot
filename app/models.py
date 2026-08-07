import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"


class LookingFor(str, enum.Enum):
    male = "male"
    female = "female"
    any = "any"


class Language(str, enum.Enum):
    uz = "uz"
    ru = "ru"
    en = "en"


class SearchScope(str, enum.Enum):
    city = "city"        # faqat o'z shahri bo'yicha qidirish
    country = "country"  # butun O'zbekiston bo'yicha qidirish


class SessionStatus(str, enum.Enum):
    active = "active"
    ended = "ended"


class User(Base):
    __tablename__ = "users"

    # Telegram user_id ni PK sifatida ishlatamiz
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[Gender] = mapped_column(Enum(Gender))
    looking_for: Mapped[LookingFor] = mapped_column(Enum(LookingFor))
    language: Mapped[Language] = mapped_column(Enum(Language), default=Language.uz)

    bio: Mapped[str | None] = mapped_column(String(300), nullable=True)  # qiziqishlar
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)  # erkin matn (masalan tuman)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)  # ro'yxatdan tanlangan shahar/viloyat
    search_scope: Mapped[SearchScope] = mapped_column(Enum(SearchScope), default=SearchScope.country)

    is_verified: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    is_in_call: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CallSession(Base):
    __tablename__ = "call_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))

    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.active)
    room_id: Mapped[str] = mapped_column(String(64))  # WebRTC/LiveKit xona nomi

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
