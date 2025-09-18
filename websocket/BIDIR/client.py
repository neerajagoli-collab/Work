import socket

c_socket = socket.socket()
c_socket.connect(('localhost', 1010))

while True:
    # Client sends custom message
    msg = input("You (Client): ")
    c_socket.send(msg.encode())

    # Receive response from server
    res = c_socket.recv(1024).decode()
    print(f"Server: {res}")