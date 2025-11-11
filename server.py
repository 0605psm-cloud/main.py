# server.py
import os, asyncio, json, websockets
from http import HTTPStatus
from collections import defaultdict

PORT = int(os.environ.get("PORT", "10000"))  # Render가 넘겨주는 포트 사용

# 연결 풀: vehicle_id 기준으로 app/client 그룹 나눔
apps     = defaultdict(set)   # /app/<vehicle_id>
vehicles = defaultdict(set)   # /ws/<vehicle_id>

def peers(kind, vid):
    return apps[vid] if kind == "app" else vehicles[vid]

async def relay(kind, vid, msg):
    # app -> vehicle, vehicle -> app 교차 전달
    targets = vehicles[vid] if kind == "app" else apps[vid]
    if not targets:
        return
    await asyncio.gather(*[t.send(msg) for t in list(targets)])

async def handler(ws, path):
    # path 라우팅: /app/<id> 또는 /ws/<id>
    # 예: wss://<your>.onrender.com/app/alpha  (앱)
    #     wss://<your>.onrender.com/ws/alpha   (라떼판다)
    kind = None
    vid  = None
    try:
        parts = [p for p in path.split("/") if p]
        if len(parts) == 2 and parts[0] in ("app", "ws"):
            kind = "app" if parts[0] == "app" else "ws"
            vid  = parts[1]
        else:
            await ws.close(code=1008, reason="Bad path")
            return

        group = apps if kind == "app" else vehicles
        group[vid].add(ws)
        print(f"✅ [{kind}] connected vid={vid}, total apps={len(apps[vid])} vehicles={len(vehicles[vid])}")

        async for raw in ws:
            # 문자열/바이너리 모두 문자열로 처리
            msg = raw.decode() if isinstance(raw, (bytes, bytearray)) else raw
            print(f"📩 [{kind}] {vid}: {msg}")
            # 그대로 반대편으로 중계
            await relay(kind, vid, msg)

    except websockets.exceptions.ConnectionClosedOK:
        pass
    except Exception as e:
        print("⚠️ handler error:", e)
    finally:
        if kind and vid:
            group = apps if kind == "app" else vehicles
            group[vid].discard(ws)
            print(f"❌ [{kind}] disconnected vid={vid}")

# Render 헬스체크(HEAD/GET /)를 200 OK로 처리
async def process_request(path, request_headers):
    # HEAD 또는 GET /, /health 에 200 OK 반환
    method = request_headers.get("Method", "")  # websockets 내부가 넣어줄 수 있음
    # websockets>=12는 request_headers에 Method가 없을 수 있으니 path만 보고 처리
    if path in ("/", "/health"):
        body = b"OK"
        headers = [("Content-Type", "text/plain"), ("Content-Length", str(len(body)))]
        return HTTPStatus.OK, headers, body

    # 그 외 경로의 **일반 HTTP** 요청도 404로 응답 (웹소켓 업그레이드는 None 반환)
    return None  # None을 반환하면 정상적인 WebSocket 업그레이드 시도

async def main():
    print(f"🚀 WebSocket listening on 0.0.0.0:{PORT}")
    async with websockets.serve(
        handler,
        host="0.0.0.0",
        port=PORT,
        process_request=process_request,  # ← 헬스체크 처리
        max_size=2**20,  # 1MB
        ping_interval=20,
        ping_timeout=20,
    ):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
