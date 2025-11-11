# server.py
import asyncio
import websockets
import json
from aiohttp import web

connected_clients = set()

async def websocket_handler(websocket):
    print("✅ 클라이언트 연결됨")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"📩 수신: {message}")
            # 그대로 echo 또는 로직 추가 가능
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        print("❌ 연결 종료")
    finally:
        connected_clients.remove(websocket)

async def start_websocket_server():
    print("🚀 WebSocket 서버 시작 ws://0.0.0.0:8765")
    async with websockets.serve(websocket_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # 무한 대기

# ✅ Render 헬스체크용 HTTP 서버
async def handle_root(request):
    return web.Response(text="Server is running ✅")

async def start_http_server():
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    print("🌐 HTTP 서버 시작 (Render Health Check용)")
    await site.start()

# ✅ 두 서버를 동시에 실행
async def main():
    await asyncio.gather(
        start_http_server(),
        start_websocket_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
