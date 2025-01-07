import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = '127.0.0.1'  # localhost
    port = 12345
    server_socket.bind((host, port))

    # Start listening for connections
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    # Accept a connection
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

# do not tuch anything above



    # Send a string to the client
    message = "Hello from Python server!"
    client_socket.sendall(message.encode('utf-8'))

    # Close the sockets
    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    start_server()
