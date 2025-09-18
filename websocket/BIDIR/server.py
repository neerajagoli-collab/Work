import socket

s_socket = socket.socket()
s_socket.bind(('localhost', 1010))
s_socket.listen(1)

print("Server is listening...")

conn, addr = s_socket.accept()
print("Connected to", addr)

while True:
    # Receive message from client
    data = conn.recv(1024).decode()
    if not data:
        break
    print(f"Client: {data}")

    # Server sends custom message
    msg = input("You (Server): ")
    conn.send(msg.encode())

conn.close()