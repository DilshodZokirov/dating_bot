"""Avatar fayllari — diskda saqlash."""

from __future__ import annotations

import os
from pathlib import Path

AVATAR_DIR = Path(os.environ.get("AVATAR_DIR", "data/avatars"))
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB


def ensure_avatar_dir() -> Path:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    return AVATAR_DIR


def avatar_path_for(user_id: int, ext: str = ".jpg") -> Path:
    ensure_avatar_dir()
    return AVATAR_DIR / f"{user_id}{ext}"


def find_avatar_file(user_id: int) -> Path | None:
    ensure_avatar_dir()
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = AVATAR_DIR / f"{user_id}{ext}"
        if p.is_file():
            return p
    return None


def avatar_url(user_id: int, has_avatar: bool) -> str | None:
    if not has_avatar:
        return None
    # cache-bust: mtime
    f = find_avatar_file(user_id)
    v = int(f.stat().st_mtime) if f else 0
    return f"/api/avatar/{user_id}?v={v}"


def delete_avatar_files(user_id: int) -> None:
    ensure_avatar_dir()
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = AVATAR_DIR / f"{user_id}{ext}"
        if p.is_file():
            p.unlink(missing_ok=True)
