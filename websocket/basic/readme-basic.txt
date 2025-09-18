Client (cl.py)
1. Uses asyncio and websockets to connect to server at ws://...:1010.
2. Accepts our(user) input from console.
3. It then sends the message to server.
4. Waits asynchronously for server’s response and prints it.

Server (sr.py)
1. Runs a WebSocket server at ...:1010.
2. On client connection, logs the remote address.
3. Handles incoming messages from clients asynchronously.
4. Sends back acknowledgment as Server received: <message>.
5. Handles disconnection gracefully using ConnectionClosed.