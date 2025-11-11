# main.py
import json, time, asyncio
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# 각 vehicle_id마다 연결된 라떼판다(=브리지) WebSocket 보관
vehicle_clients: Dict[str, Set[WebSocket]] = {}
# 앱(모바일) 클라이언트도 원하면 보관 가능 (여기선 옵션)
app_clients: Dict[str, Set[WebSocket]] = {}

def _get_room(d: Dict[str, Set[WebSocket]], key: str) -> Set[WebSocket]:
    if key not in d: d[key] = set()
    return d[key]

@app.get("/")
def health():
    return {"ok": True, "ts": int(time.time())}

@app.websocket("/ws/{vehicle_id}")
async def ws_endpoint(websocket: WebSocket, vehicle_id: str):
    await websocket.accept()
    room = _get_room(vehicle_clients, vehicle_id)
    room.add(websocket)
    try:
        # 주기적 ping으로 프록시/방화벽에서 연결이 죽지 않도록 유지
        ping_task = asyncio.create_task(_ping_forever(websocket))
        while True:
            raw = await websocket.receive_text()
            # 라떼판다가 뭔가 보내면 앱들에게도 브로드캐스트할 수 있음(옵션)
            await _broadcast(app_clients.get(vehicle_id, set()), raw)
    except WebSocketDisconnect:
        pass
    finally:
        room.discard(websocket)

@app.websocket("/app/{vehicle_id}")
async def ws_app(websocket: WebSocket, vehicle_id: str):
    await websocket.accept()
    room = _get_room(app_clients, vehicle_id)
    room.add(websocket)
    try:
        ping_task = asyncio.create_task(_ping_forever(websocket))
        while True:
            raw = await websocket.receive_text()
            # 앱 → 서버로 온 메시지를 차량(라떼판다)에게 전달
            await _broadcast(vehicle_clients.get(vehicle_id, set()), raw)
    except WebSocketDisconnect:
        pass
    finally:
        room.discard(websocket)

async def _broadcast(peers: Set[WebSocket], raw: str):
    dead = []
    for ws in peers:
        try:
            await ws.send_text(raw)
        except Exception:
            dead.append(ws)
    for ws in dead:
        peers.discard(ws)

async def _ping_forever(ws: WebSocket, interval: int = 25):
    # 유휴 연결이 중간에서 끊기지 않도록 ping 역할 (텍스트 keepalive)
    while True:
        try:
            await ws.send_text(json.dumps({"type":"ping","ts":int(time.time())}))
        except Exception:
            return
        await asyncio.sleep(interval)
