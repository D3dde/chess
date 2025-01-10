import socket
import chess
import random

class ChessServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 12345))
        self.server.listen(1)
        self.board = chess.Board()

    def handleClient(self, clientSocket):
        try:
            clientSocket.send((self.board.fen() + "\n").encode('utf-8'))
            print(f"Sent FEN: {self.board.fen()}")

            while not self.board.is_game_over():
                # riceve
                move = clientSocket.recv(1024).decode('utf-8').strip()
                print(f"Move received: {move}")
                # invia
                if self.isValid(move):
                    # player
                    self.board.push(chess.Move.from_uci(move))
                    # pc
                    self.board.push(random.choice(list(self.board.legal_moves)))
                    clientSocket.send((self.board.fen() + "\n").encode('utf-8'))
                    print(f"Sent FEN: {self.board.fen()}")
                else:
                    clientSocket.send(b"Invalid move. Try again.\n")
            # game over
            result = self.board.result()
            clientSocket.send((f"Game over! Result: {result}\n").encode('utf-8'))

        except ConnectionError:
            print("Client disconnected.")
        finally:
            clientSocket.close()

    def isValid(self, move):
        return chess.Move.from_uci(move) in self.board.legal_moves

    def start(self):
        print("Chess server started...")
        clientSocket, address = self.server.accept()
        print(f"Connected")
        self.handleClient(clientSocket)

if __name__ == "__main__":
    chessServer = ChessServer()
    chessServer.start()