import asyncio
import websockets
import json
import threading
import random
import chess

# Chess Game
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
                    if not self.board.is_game_over():
                        computer_move = self.get_computer_move()
                        self.board.push(computer_move)
                    return True
                return False
            except ValueError:
                return False

    def get_computer_move(self):
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


async def handle_connection(websocket):
    print(f"Client connected : ip {websocket.remote_address[0]}")
    # new game
    game = ChessGame()
    try:
        # init
        await send_json(websocket, {"command": "fen","value": game.get_fen()})

        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")

                if command == "move":
                    move_uci = data.get("value")
                    game.make_move(move_uci)

                    await send_json(websocket,{"command": "fen","value": game.get_fen()})

                    # game over check
                    if game.is_game_over():
                        await send_json(websocket,{"command": "gameover","value": game.result()})

            except json.JSONDecodeError:
                print("Invalid JSON received")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected abnormally")
    finally:
        print("Client disconnected normally")

async def send_json(websocket, data):
    json_string = json.dumps(data)
    await websocket.send(json_string)

async def main():
    server = await websockets.serve(handle_connection, "localhost", 8888)
    print("Chess server started at ws://localhost:8888")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
