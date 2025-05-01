
import asyncio
import websockets
import json
import threading
import random
import chess

# Chess game state
class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.lock = threading.Lock()

    def make_move(self, move_uci):
        with self.lock:
            try:
                move = chess.Move.from_uci(move_uci)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    # Make computer move
                    if not self.board.is_game_over():
                        computer_move = self.get_computer_move()
                        self.board.push(computer_move)
                    return True
                return False
            except ValueError:
                return False

    def get_computer_move(self):
        # Simple random move strategy
        legal_moves = list(self.board.legal_moves)
        return random.choice(legal_moves)

    def get_fen(self):
        with self.lock:
            return self.board.fen()

    def is_game_over(self):
        with self.lock:
            return self.board.is_game_over()

    def result(self):
        with self.lock:
            return self.board.result()

# Global game state
game = ChessGame()

# Handle WebSocket connections
async def handle_connection(websocket):
    try:
        # Send initial board state
        await websocket.send(json.dumps({
            "command": "fen",
            "value": game.get_fen()
        }))

        # Process messages
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")

                if command == "move":
                    move_uci = data.get("value")
                    success = game.make_move(move_uci)

                    # Send updated FEN after move
                    await websocket.send(json.dumps({
                        "command": "fen",
                        "value": game.get_fen()
                    }))

                    # Check for game over
                    if game.is_game_over():
                        await websocket.send(json.dumps({
                            "command": "gameover",
                            "value": game.result()
                        }))

                elif command == "reset":
                    game.__init__()  # Reset the game
                    await websocket.send(json.dumps({
                        "command": "fen",
                        "value": game.get_fen()
                    }))

            except json.JSONDecodeError:
                print("Invalid JSON received")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    # Start WebSocket server
    server = await websockets.serve(handle_connection, "localhost", 8888)
    print("Chess server started at ws://localhost:8888")

    # Keep the server running
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
