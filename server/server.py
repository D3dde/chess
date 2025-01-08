import socket
import threading
import chess  # python-chess library for game logic

class ChessServer:
    def __init__(self, host='127.0.0.1', port=65432):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.clients = []
        self.board = chess.Board()

    def handle_client(self, client_socket):
        try:
            client_socket.send(str(self.board).encode('utf-8'))
            while not self.board.is_game_over():
                move = client_socket.recv(1024).decode('utf-8').strip()
                if self.is_valid_move(move):
                    self.board.push(chess.Move.from_uci(move))
                    client_socket.send(str(self.board).encode('utf-8'))
                else:
                    client_socket.send(b"Invalid move. Try again.\n")
            client_socket.send(b"Game over!\n")
        except ConnectionError:
            print("Client disconnected.")
        finally:
            client_socket.close()

    def is_valid_move(self, move):
        try:
            return chess.Move.from_uci(move) in self.board.legal_moves
        except ValueError:
            return False

    def start(self):
        print("Chess server started...")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Connection from {addr}")
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = ChessServer()
    server.start()
