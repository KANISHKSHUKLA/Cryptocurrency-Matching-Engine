import asyncio
import websockets
import json

async def connect_market_data():
    uri = "ws://localhost:8000/ws/market-data"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print("Market Data:", json.loads(data))

async def connect_trades():
    uri = "ws://localhost:8000/ws/trades"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print("Trade:", json.loads(data))

async def main():
    await asyncio.gather(
        connect_market_data(),
        connect_trades()
    )

if __name__ == "__main__":
    asyncio.run(main())