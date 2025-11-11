import os, uuid, time
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN", "CHANGE_ME")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vehicle_ws: Dict[str, WebSocket] = {}

class Command(BaseModel):
    vehicleId: str
    stopId: int
    requestId: str | None = None
    deadlineMs: int = 60000

def auth(b: str | None):
    if b != f"Bearer {API_TOKEN}":
        raise HTTPException(401, "Unauthorized")

@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": datetime.now().timestamp()}

@app.get("/")
def root():
    return {"ok": True, "ts": datetime.now().timestamp(), "message": "Hello from Cloud Run!"}
    
@app.post("/command")
async def command(cmd: Command, authorization: str | None = Header(None)):
    auth(authorization)
    if cmd.stopId not in (1, 2):
        raise HTTPException(400, "stopId must be 1 or 2")
    ws = vehicle_ws.get(cmd.vehicleId)
    if not ws:
        raise HTTPException(409, "Vehicle offline")
    rid = cmd.requestId or str(uuid.uuid4())
    await ws.send_json(
        {"type": "command", "cmd": "GO_TO_STOP", "stopId": cmd.stopId, "requestId": rid}
    )
    return {"accepted": True, "requestId": rid}

@app.websocket("/ws/vehicle/{vehicleId}")
async def vehicle_ws_handler(ws: WebSocket, vehicleId: str):
    await ws.accept()
    vehicle_ws[vehicleId] = ws
    try:
        while True:
            _ = await ws.receive_json()  # 차량 이벤트 수신(추후 확장)
    except WebSocketDisconnect:
        pass
    finally:
        vehicle_ws.pop(vehicleId, None)
