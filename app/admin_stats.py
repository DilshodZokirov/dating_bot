"""Admin statistikasi — umumiy foydalanuvchilar, viloyatlar bo‘yicha."""

from __future__ import annotations

from sqlalchemy import func, select

from app.cities import UZBEKISTAN_CITIES
from app.database import async_session
from app.models import CallSession, ChatThread, Report, ReportStatus, SessionStatus, User


async def collect_admin_stats() -> dict:
    async with async_session() as session:
        users_count = (await session.execute(select(func.count()).select_from(User))).scalar() or 0
        banned_count = (
            await session.execute(select(func.count()).select_from(User).where(User.is_banned.is_(True)))
        ).scalar() or 0
        open_reports = (
            await session.execute(
                select(func.count()).select_from(Report).where(Report.status == ReportStatus.open)
            )
        ).scalar() or 0
        active_calls = (
            await session.execute(
                select(func.count()).select_from(CallSession).where(CallSession.status == SessionStatus.active)
            )
        ).scalar() or 0
        threads_count = (await session.execute(select(func.count()).select_from(ChatThread))).scalar() or 0

        city_rows = (
            await session.execute(
                select(User.city, func.count())
                .group_by(User.city)
                .order_by(func.count().desc())
            )
        ).all()

        gender_rows = (
            await session.execute(select(User.gender, func.count()).group_by(User.gender))
        ).all()

        lang_rows = (
            await session.execute(
                select(User.language, func.count())
                .group_by(User.language)
                .order_by(func.count().desc())
            )
        ).all()

        with_avatar = (
            await session.execute(
                select(func.count()).select_from(User).where(User.has_avatar.is_(True))
            )
        ).scalar() or 0

    by_city_map: dict[str, int] = {}
    no_city = 0
    for city, cnt in city_rows:
        n = int(cnt)
        if not city or not str(city).strip():
            no_city += n
        else:
            by_city_map[str(city)] = by_city_map.get(str(city), 0) + n

    # Ro‘yxatdagi viloyatlar tartibida + boshqalar
    by_city: list[dict] = []
    seen: set[str] = set()
    for name in UZBEKISTAN_CITIES:
        c = int(by_city_map.get(name, 0))
        by_city.append({"city": name, "count": c})
        seen.add(name)
    extras = sorted(
        ((k, v) for k, v in by_city_map.items() if k not in seen),
        key=lambda x: (-x[1], x[0]),
    )
    for name, c in extras:
        by_city.append({"city": name, "count": int(c)})
    if no_city:
        by_city.append({"city": "— (ko‘rsatilmagan)", "count": no_city})

    by_gender = [
        {
            "gender": g.value if hasattr(g, "value") else str(g),
            "count": int(cnt),
        }
        for g, cnt in gender_rows
    ]
    by_language = [
        {
            "language": lang.value if hasattr(lang, "value") else str(lang),
            "count": int(cnt),
        }
        for lang, cnt in lang_rows
    ]

    return {
        "users": users_count,
        "banned": banned_count,
        "open_reports": open_reports,
        "active_calls": active_calls,
        "chat_threads": threads_count,
        "with_avatar": with_avatar,
        "by_city": by_city,
        "by_gender": by_gender,
        "by_language": by_language,
    }


def format_stats_html(stats: dict) -> str:
    lines = [
        "📊 <b>Statistika</b>\n",
        f"👥 Jami foydalanuvchilar: <b>{stats.get('users', 0)}</b>",
        f"🚫 Ban: <b>{stats.get('banned', 0)}</b>",
        f"🖼 Avatar: <b>{stats.get('with_avatar', 0)}</b>",
        f"🚨 Ochiq shikoyat: <b>{stats.get('open_reports', 0)}</b>",
        f"💬 Chatlar: <b>{stats.get('chat_threads', 0)}</b>",
        f"📞 Faol qo‘ng‘iroq (soni): <b>{stats.get('active_calls', 0)}</b>",
        "",
        "<b>Viloyat / shahar:</b>",
    ]
    for row in stats.get("by_city") or []:
        if int(row.get("count") or 0) <= 0 and row.get("city") in set(UZBEKISTAN_CITIES):
            continue  # bo‘sh viloyatlarni botda yashirish (qisqaroq)
        lines.append(f"· {row['city']}: <b>{row['count']}</b>")

    if stats.get("by_gender"):
        lines.append("")
        lines.append("<b>Jins:</b>")
        for row in stats["by_gender"]:
            g = row["gender"]
            label = "Erkak" if g == "male" else ("Ayol" if g == "female" else g)
            lines.append(f"· {label}: <b>{row['count']}</b>")

    if stats.get("by_language"):
        lines.append("")
        lines.append("<b>Til:</b>")
        for row in stats["by_language"]:
            lines.append(f"· {row['language']}: <b>{row['count']}</b>")

    return "\n".join(lines)
