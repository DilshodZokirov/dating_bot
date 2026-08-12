"""Matching filterlari — Redis/settings'siz."""

import os

os.environ.setdefault("BOT_TOKEN", "test")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.matching.age_brackets import default_prefer_ages
from app.matching.queue import _age_pref_compatible, _city_compatible


def test_default_prefer_ages_is_open():
    assert default_prefer_ages(22) == (18, 99)
    assert default_prefer_ages(45) == (18, 99)


def test_age_pref_mutual():
    assert _age_pref_compatible(22, 18, 99, 30, 18, 99)
    assert not _age_pref_compatible(22, 20, 24, 30, 25, 29)
    assert _age_pref_compatible(22, 20, 30, 28, 18, 25)


def test_city_scope():
    assert _city_compatible("Toshkent", "country", "Samarqand", "country")
    assert not _city_compatible("Toshkent", "city", "Samarqand", "country")
    assert _city_compatible("Toshkent", "city", "Toshkent", "city")
