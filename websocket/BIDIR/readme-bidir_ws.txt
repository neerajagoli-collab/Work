Client (client.py)
1. Creates a TCP socket and connects to server (localhost:1010).
2. Takes custom input from user (input("You (Client): ")).
3. Sends message to server using send().
4. Waits for response from server using recv(1024) and prints it.

Server (server.py)
1. Creates a TCP socket and binds it to localhost:1010.
2. Starts listening for incoming connections with listen.
3. Accepts a client connection (accept()).
4. Enters loop to continuously: Receive client messages,Print them and 
    Send a custom response entered by server user.

