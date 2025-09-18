import asyncio
import websockets

async def run_client():
    uri = "ws://localhost:1010"
    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        while True:
            msg = input("You: ")
            await websocket.send(msg)  # send to server
            reply = await websocket.recv()  # wait for reply
            print(f"Server: {reply}")

asyncio.run(run_client())
