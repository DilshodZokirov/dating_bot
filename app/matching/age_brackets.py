"""
Yosh oralig'i — foydalanuvchi quyi/yuqori chegarani o'zi tanlaydi (0–100).
Minimal o'z yoshi — settings.min_age (default 12).
"""

PREFER_AGE_FLOOR = 0
PREFER_AGE_CEIL = 100


def default_prefer_ages(age: int | None = None) -> tuple[int, int]:
    """Ro'yxatdan o'tganda default: keng oraliq."""
    return 12, 100


def age_range_options() -> list[dict]:
    """API: UI uchun chegara ma'lumotlari (bracket emas)."""
    return []


def prefer_bounds_meta(min_age: int = 12) -> dict:
    return {
        "min_age": min_age,
        "prefer_floor": PREFER_AGE_FLOOR,
        "prefer_ceil": PREFER_AGE_CEIL,
        "default_min": 12,
        "default_max": 100,
    }


def clamp_prefer(
    age_min: int,
    age_max: int,
    min_age: int = 12,
    floor: int = PREFER_AGE_FLOOR,
    ceil: int = PREFER_AGE_CEIL,
) -> tuple[int, int]:
    """Quyi/yuqori — foydalanuvchi tanlovi; faqat 0–100 va tartibni ta'minlaymiz."""
    lo = int(age_min)
    hi = int(age_max)
    if hi < lo:
        lo, hi = hi, lo
    lo = max(floor, min(lo, ceil))
    hi = max(floor, min(hi, ceil))
    if hi < lo:
        hi = lo
    return lo, hi
