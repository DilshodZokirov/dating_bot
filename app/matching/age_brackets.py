"""
Yosh oraliqlari (bracket'lar). Foydalanuvchilar faqat bir xil oraliqdagilar bilan
moslashadi — masalan 18 yoshli foydalanuvchi 50 yoshli bilan moslashmaydi.
"""

AGE_BRACKETS = [
    (18, 19),
    (20, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 49),
    (50, 59),
    (60, 120),
]


def age_bracket(age: int) -> str:
    for low, high in AGE_BRACKETS:
        if low <= age <= high:
            return f"{low}-{high}"
    return "60-120"
