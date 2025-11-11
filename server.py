import asyncio
import websockets
from aiohttp import web

# =============== WebSocket Handler ===============
async def handler(websocket):
    print("✅ 클라이언트가 연결되었습니다.")
    try:
        async for message in websocket:
            print(f"📩 수신: {message}")
            await websocket.send(f"서버 응답: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("❌ 연결이 종료되었습니다.")

# =============== HTTP Health Check ===============
async def healthcheck(request):
    return web.Response(text="OK")  # Render가 여기로 HEAD/GET 보냄

async def start_websocket():
    print("🚀 WebSocket 서버 시작: ws://0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

async def start_http():
    app = web.Application()
    app.router.add_get("/", healthcheck)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)  # Render의 기본 포트
    await site.start()
    print("🌐 HTTP 헬스체크 서버 시작: http://0.0.0.0:10000")

async def main():
    await asyncio.gather(start_http(), start_websocket())

asyncio.run(main())
