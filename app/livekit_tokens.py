"""LiveKit AccessToken yaratish."""

from datetime import timedelta

from livekit import api

from app.config import settings


def livekit_configured() -> bool:
    return bool(settings.livekit_url and settings.livekit_api_key and settings.livekit_api_secret)


def create_room_token(*, identity: str, name: str, room_id: str, ttl_hours: int = 2) -> str:
    if not livekit_configured():
        raise RuntimeError("LiveKit sozlanmagan (LIVEKIT_URL / API_KEY / API_SECRET)")

    return (
        api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_name(name or identity)
        .with_ttl(timedelta(hours=ttl_hours))
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_id,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )


def livekit_join_payload(*, identity: str, name: str, room_id: str) -> dict:
    return {
        "livekit_url": settings.livekit_url,
        "livekit_token": create_room_token(identity=identity, name=name, room_id=room_id),
        "room_id": room_id,
    }
