import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
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
    de = "de"
    tg = "tg"  # tojik
    tr = "tr"  # turk
    ko = "ko"  # koreys
    ja = "ja"  # yapon
    zh = "zh"  # xitoy
    ar = "ar"  # arab


class SearchScope(str, enum.Enum):
    city = "city"        # faqat o'z shahri bo'yicha qidirish
    country = "country"  # butun O'zbekiston bo'yicha qidirish


class SessionStatus(str, enum.Enum):
    active = "active"
    ended = "ended"


class ReportReason(str, enum.Enum):
    spam = "spam"
    harassment = "harassment"
    inappropriate = "inappropriate"
    underage = "underage"
    other = "other"


class ReportStatus(str, enum.Enum):
    open = "open"
    reviewed = "reviewed"
    dismissed = "dismissed"


class User(Base):
    __tablename__ = "users"

    # Telegram user_id ni PK sifatida ishlatamiz
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[Gender] = mapped_column(Enum(Gender))
    looking_for: Mapped[LookingFor] = mapped_column(Enum(LookingFor))
    # Matching / suhbat tili (aloqa sozlamalari)
    language: Mapped[Language] = mapped_column(Enum(Language), default=Language.uz)
    # Mini App + bot interfeys tili (profil)
    ui_language: Mapped[Language] = mapped_column(
        Enum(Language, name="language", create_type=False),
        default=Language.uz,
    )

    bio: Mapped[str | None] = mapped_column(String(300), nullable=True)  # qiziqishlar
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)  # erkin matn (masalan tuman)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)  # ro'yxatdan tanlangan shahar/viloyat
    search_scope: Mapped[SearchScope] = mapped_column(Enum(SearchScope), default=SearchScope.country)

    # Profil rasmi: data/avatars/{id}.jpg|png|webp
    has_avatar: Mapped[bool] = mapped_column(default=False)

    # Mavzuli match: friends | dating | study | any (til — Language maydonida)
    match_topic: Mapped[str] = mapped_column(String(32), default="any")

    # Aloqa sozlamalari — suhbatdosh yoshi oralig'i (foydalanuvchi o'zi 0–100)
    prefer_age_min: Mapped[int] = mapped_column(Integer, default=12)
    prefer_age_max: Mapped[int] = mapped_column(Integer, default=100)

    is_verified: Mapped[bool] = mapped_column(default=False)
    is_banned: Mapped[bool] = mapped_column(default=False)
    is_in_call: Mapped[bool] = mapped_column(default=False)
    # Telegram contact orqali ulashilgan telefon (ixtiyoriy)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # Foydalanish shartlari qabul qilingan vaqt
    terms_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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


class CallFeedback(Base):
    """Suhbatdan keyin 1–5 yulduz baho."""

    __tablename__ = "call_feedback"
    __table_args__ = (UniqueConstraint("room_id", "from_user_id", name="uq_feedback_room_from"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(64), index=True)
    from_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    to_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    stars: Mapped[int] = mapped_column(Integer)  # 1..5
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Block(Base):
    """Foydalanuvchi boshqa foydalanuvchini bloklagan."""

    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id", name="uq_block_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blocker_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    blocked_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    """Shikoyat — admin ko'rib chiqadi."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    reported_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    room_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[ReportReason] = mapped_column(Enum(ReportReason), default=ReportReason.other)
    details: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.open)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SavedPartner(Base):
    """Foydalanuvchi saqlagan suhbatdosh."""

    __tablename__ = "saved_partners"
    __table_args__ = (UniqueConstraint("user_id", "partner_id", name="uq_saved_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    partner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatInviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    cancelled = "cancelled"


class ChatInvite(Base):
    """Sevimlilar / chatga taklif — ikkinchi tomon rozilik bersa ochiladi."""

    __tablename__ = "chat_invites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    to_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    status: Mapped[ChatInviteStatus] = mapped_column(
        Enum(ChatInviteStatus), default=ChatInviteStatus.pending, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ChatThread(Base):
    """Ikki foydalanuvchi o‘rtasidagi matn chat (user_a_id < user_b_id)."""

    __tablename__ = "chat_threads"
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id", name="uq_chat_thread_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_a_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    user_b_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_threads.id"), index=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    body: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PhoneShareStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class PhoneShareRequest(Base):
    """Qo‘ng‘iroq davomida telefon raqam so‘rovi."""

    __tablename__ = "phone_share_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(64), index=True)
    from_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    to_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    status: Mapped[PhoneShareStatus] = mapped_column(
        Enum(PhoneShareStatus), default=PhoneShareStatus.pending, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

