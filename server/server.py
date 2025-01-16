import socket
import chess
import random
import threading

class ChessServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.board = chess.Board()
        self.lock = threading.Lock()  # Ensures synchronization on the board

    def handleClient(self, clientSocket):
        try:
            # Send initial board state to the client
            clientSocket.send((self.board.fen() + "\n").encode('utf-8'))
            print(f"Sent FEN: {self.board.fen()}")

            # Player and computer threads
            player_thread = threading.Thread(target=self.handlePlayer, args=(clientSocket,))
            computer_thread = threading.Thread(target=self.handleComputer, args=(clientSocket,))

            # Start threads
            player_thread.start()
            computer_thread.start()

            # Wait for both threads to finish
            player_thread.join()
            computer_thread.join()

        except ConnectionError:
            print("Client disconnected.")
        finally:
            clientSocket.close()

    def handlePlayer(self, clientSocket):
        while not self.board.is_game_over():
            try:
                move = clientSocket.recv(1024).decode('utf-8').strip()
                print(f"Move received: {move}")

                with self.lock:  # Synchronize board access
                    if self.isValid(move):
                        self.board.push(chess.Move.from_uci(move))
                        print(f"Player move applied: {move}")
            except Exception as e:
                print(f"Error in player thread: {e}")
                break

    def handleComputer(self, clientSocket):
        while not self.board.is_game_over():
            with self.lock:  # Synchronize board access
                if not self.board.turn:  # It's computer's turn
                    move = random.choice(list(self.board.legal_moves))
                    self.board.push(move)
                    print(f"Computer move applied: {move}")
                    clientSocket.send((self.board.fen() + "\n").encode('utf-8'))

    def isValid(self, move):
        try:
            return chess.Move.from_uci(move) in self.board.legal_moves
        except:
            return False

    def start(self):
        print("Chess server started...")
        while True:
            clientSocket, address = self.server.accept()
            print(f"Connected to {address}")
            client_handler = threading.Thread(target=self.handleClient, args=(clientSocket,))
            client_handler.start()

if __name__ == "__main__":
    chessServer = ChessServer()
    chessServer.start()