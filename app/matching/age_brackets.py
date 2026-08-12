"""
Yosh oraliqlari — sozlamalarda tanlanadi va matchingda qo'llaniladi.
"""

AGE_BRACKETS = [
    (18, 19),
    (20, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 49),
    (50, 59),
    (60, 99),
]


def age_bracket(age: int) -> str:
    for low, high in AGE_BRACKETS:
        if low <= age <= high:
            return f"{low}-{high}"
    return "60-99"


def default_prefer_ages(age: int) -> tuple[int, int]:
    """Ro'yxatdan o'tganda default: barcha yoshlar (18+)."""
    return 18, 99


def age_range_options() -> list[dict]:
    """API / UI uchun ro'yxat."""
    opts = [{"id": "any", "min": 18, "max": 99, "label": "18+ (hammasi)"}]
    for low, high in AGE_BRACKETS:
        opts.append({"id": f"{low}-{high}", "min": low, "max": high, "label": f"{low}–{high}"})
    return opts


def clamp_prefer(age_min: int, age_max: int, min_age: int = 18) -> tuple[int, int]:
    lo = max(min_age, min(age_min, age_max))
    hi = min(99, max(age_min, age_max))
    if hi < lo:
        hi = lo
    return lo, hi
