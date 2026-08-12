"""
WebRTC signaling — ikkala foydalanuvchi brauzeri o'rtasida SDP/ICE xabarlarini
almashtirib beruvchi oddiy WebSocket relay.
"""

import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app import test_mode
from app.telegram_auth import InitDataError, validate_init_data

router = APIRouter()

# room_id -> {user_id: WebSocket}
_rooms: dict[str, dict[int, WebSocket]] = {}


@router.websocket("/ws/call/{room_id}")
async def call_signaling(
    websocket: WebSocket,
    room_id: str,
    init_data: str | None = Query(default=None),
    test_token: str | None = Query(default=None),
):
    user_id: int | None = None

    if test_token:
        try:
            claims = test_mode.verify_test_token(test_token, expected_room_id=room_id)
            user_id = claims["user_id"]
        except ValueError:
            await websocket.close(code=4001)
            return
    elif init_data:
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
    # eski ulanishni almashtirish
    room[user_id] = websocket

    others = [uid for uid in room.keys() if uid != user_id]
    join_msg = json.dumps({"type": "peer-joined", "user_id": user_id, "peers": len(room)})
    for uid in others:
        try:
            await room[uid].send_text(join_msg)
        except Exception:
            pass
    if others:
        # yangi kelganga ham "allaqachon kimdir bor" deb xabar
        try:
            await websocket.send_text(
                json.dumps({"type": "peer-joined", "user_id": others[0], "peers": len(room)})
            )
        except Exception:
            pass

    try:
        while True:
            data = await websocket.receive_text()
            for uid, ws in list(room.items()):
                if uid != user_id:
                    try:
                        await ws.send_text(data)
                    except Exception:
                        pass
    except WebSocketDisconnect:
        pass
    finally:
        if room.get(user_id) is websocket:
            room.pop(user_id, None)
        if not room:
            _rooms.pop(room_id, None)
        else:
            leave_msg = json.dumps({"type": "peer-left", "user_id": user_id, "peers": len(room)})
            for ws in list(room.values()):
                try:
                    await ws.send_text(leave_msg)
                except Exception:
                    pass
