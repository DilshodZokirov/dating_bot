"""
WebRTC signaling — ikkala foydalanuvchi brauzeri o'rtasida SDP/ICE xabarlarini
almashtirib beruvchi oddiy WebSocket relay.
"""

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.telegram_auth import InitDataError, validate_init_data

router = APIRouter()

# room_id -> {user_id: WebSocket}
_rooms: dict[str, dict[int, WebSocket]] = {}


@router.websocket("/ws/call/{room_id}")
async def call_signaling(
    websocket: WebSocket,
    room_id: str,
    init_data: str | None = Query(default=None),
):
    user_id: int | None = None

    if init_data:
        try:
            tg_user = validate_init_data(init_data)
            user_id = tg_user["id"]
        except InitDataError:
            await websocket.close(code=4001)
            return
    else:
        await websocket.close(code=4001)
        return

    await websocket.accept()

    room = _rooms.setdefault(room_id, {})
    room[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            for uid, ws in list(room.items()):
                if uid != user_id:
                    await ws.send_text(data)
    except WebSocketDisconnect:
        pass
    finally:
        room.pop(user_id, None)
        if not room:
            _rooms.pop(room_id, None)
