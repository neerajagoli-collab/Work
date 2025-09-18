import asyncio
import websockets

async def handler(websocket):
    print(f"Client connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"Received from client: {message}")
            response = f"Server received: {message}"
            await websocket.send(response)
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

# Run the server
async def main():
    async with websockets.serve(handler, "localhost", 1010):
        print("WebSocket server running at ws://localhost:1010")
        await asyncio.Future()  

asyncio.run(main())
