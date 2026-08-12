"""Bloklash / shikoyat yordamchilari."""

from sqlalchemy import or_, select

from app.database import async_session
from app.models import Block, Report, ReportReason, ReportStatus, User


async def get_blocked_ids(user_id: int) -> set[int]:
    """user_id bloklagan YOKI uni bloklaganlar — matchingda o'tkazib yuboriladi."""
    async with async_session() as session:
        rows = await session.execute(
            select(Block.blocker_id, Block.blocked_id).where(
                or_(Block.blocker_id == user_id, Block.blocked_id == user_id)
            )
        )
        blocked: set[int] = set()
        for blocker_id, blocked_id in rows.all():
            if blocker_id == user_id:
                blocked.add(blocked_id)
            else:
                blocked.add(blocker_id)
        return blocked


async def is_blocked_pair(a: int, b: int) -> bool:
    async with async_session() as session:
        row = await session.execute(
            select(Block.id).where(
                or_(
                    (Block.blocker_id == a) & (Block.blocked_id == b),
                    (Block.blocker_id == b) & (Block.blocked_id == a),
                )
            ).limit(1)
        )
        return row.scalar_one_or_none() is not None


async def add_block(blocker_id: int, blocked_id: int) -> bool:
    if blocker_id == blocked_id:
        return False
    async with async_session() as session:
        existing = await session.execute(
            select(Block).where(Block.blocker_id == blocker_id, Block.blocked_id == blocked_id)
        )
        if existing.scalar_one_or_none():
            return True
        session.add(Block(blocker_id=blocker_id, blocked_id=blocked_id))
        await session.commit()
        return True


async def add_report(
    reporter_id: int,
    reported_id: int,
    reason: ReportReason,
    details: str | None = None,
    room_id: str | None = None,
) -> Report:
    async with async_session() as session:
        report = Report(
            reporter_id=reporter_id,
            reported_id=reported_id,
            reason=reason,
            details=(details or "")[:500] or None,
            room_id=room_id,
            status=ReportStatus.open,
        )
        session.add(report)
        await session.commit()
        await session.refresh(report)
        return report


async def list_open_reports(limit: int = 20) -> list[Report]:
    async with async_session() as session:
        rows = await session.execute(
            select(Report).where(Report.status == ReportStatus.open).order_by(Report.id.desc()).limit(limit)
        )
        return list(rows.scalars().all())


async def get_banned_ids() -> set[int]:
    async with async_session() as session:
        rows = await session.execute(select(User.id).where(User.is_banned.is_(True)))
        return set(rows.scalars().all())


async def set_user_banned(user_id: int, banned: bool) -> User | None:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return None
        user.is_banned = banned
        await session.commit()
        await session.refresh(user)
        return user


async def mark_report(report_id: int, status: ReportStatus) -> Report | None:
    async with async_session() as session:
        report = await session.get(Report, report_id)
        if not report:
            return None
        report.status = status
        await session.commit()
        await session.refresh(report)
        return report
