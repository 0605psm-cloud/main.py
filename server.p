import asyncio
import websockets

async def handler(websocket):
    print("✅ 클라이언트 연결됨")
    try:
        async for message in websocket:
            print(f"📩 수신: {message}")
            await websocket.send(f"서버 응답: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("❌ 연결 종료")

async def main():
    print("🚀 WebSocket 서버 시작 (Render)")
    async with websockets.serve(handler, "0.0.0.0", 10000):
        await asyncio.Future()  # 무한 대기

if __name__ == "__main__":
    asyncio.run(main())
