"""
WebRTC signaling — ikkala foydalanuvchi brauzeri o'rtasida SDP/ICE xabarlarini
almashtirib beruvchi oddiy WebSocket relay. Media (ovoz/video) o'zi to'g'ridan-to'g'ri
brauzerlar orasida (peer-to-peer) oqadi — bu server faqat "tanishtiruv" vazifasini
bajaradi.

ESLATMA: bu yerda faqat STUN ishlatilgan (TURN server yo'q). Ko'pchilik tarmoqlarda
ishlaydi, lekin ba'zi mobil operator tarmoqlari (carrier-grade NAT) yoki qattiq
firewall ortida ulanish muvaffaqiyatsiz bo'lishi mumkin — bunday holda TURN server
qo'shish kerak bo'ladi.
"""

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.telegram_auth import InitDataError, validate_init_data

router = APIRouter()

# room_id -> {user_id: WebSocket}
_rooms: dict[str, dict[int, WebSocket]] = {}


@router.websocket("/ws/call/{room_id}")
async def call_signaling(websocket: WebSocket, room_id: str, init_data: str = Query(...)):
    try:
        tg_user = validate_init_data(init_data)
    except InitDataError:
        await websocket.close(code=4001)
        return

    user_id = tg_user["id"]
    await websocket.accept()

    room = _rooms.setdefault(room_id, {})
    room[user_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            # xonadagi boshqa ishtirokchi(lar)ga uzatamiz
            for uid, ws in list(room.items()):
                if uid != user_id:
                    await ws.send_text(data)
    except WebSocketDisconnect:
        pass
    finally:
        room.pop(user_id, None)
        if not room:
            _rooms.pop(room_id, None)
