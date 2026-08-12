"""Online presence — Mini App ochiq bo'lsa Redis TTL bilan belgilanadi."""

from app.matching.queue import redis_client

PRESENCE_TTL_SECONDS = 45
PRESENCE_PREFIX = "presence:"


def _key(user_id: int) -> str:
    return f"{PRESENCE_PREFIX}{user_id}"


async def touch_presence(user_id: int) -> None:
    await redis_client.set(_key(user_id), "1", ex=PRESENCE_TTL_SECONDS)


async def is_online(user_id: int) -> bool:
    return bool(await redis_client.exists(_key(user_id)))


async def online_map(user_ids: list[int]) -> dict[int, bool]:
    out: dict[int, bool] = {}
    for uid in user_ids:
        out[uid] = await is_online(uid)
    return out
