import asyncio
import websockets
import json
import threading
import random
import chess
from typing import Dict, Set, Optional

# Chess Game for Singleplayer
class SingleplayerChessGame:
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


# Chess Game for Multiplayer
class MultiplayerChessGame:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.board = chess.Board()
        self.lock = threading.Lock()
        self.players: Dict[str, websockets.WebSocketServerProtocol] = {}  # 'white' or 'black' -> websocket
        self.current_turn = 'white'  # white starts first
        self.spectators: Set[websockets.WebSocketServerProtocol] = set()

    def add_player(self, websocket) -> Optional[str]:
        with self.lock:
            if 'white' not in self.players:
                self.players['white'] = websocket
                return 'white'
            elif 'black' not in self.players:
                self.players['black'] = websocket
                return 'black'
            else:
                # Game is full, add as spectator
                self.spectators.add(websocket)
                return None

    def remove_player(self, websocket):
        with self.lock:
            for color, ws in list(self.players.items()):
                if ws == websocket:
                    del self.players[color]
                    break
            self.spectators.discard(websocket)

    def make_move(self, move_uci: str, player_websocket) -> bool:
        with self.lock:
            # Find which color is making the move
            player_color = None
            for color, ws in self.players.items():
                if ws == player_websocket:
                    player_color = color
                    break
            
            if player_color is None:
                return False  # Player not found
            

            if player_color != self.current_turn:
                return False  # Not their turn
            
            try:
                move = chess.Move.from_uci(move_uci)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    # Switch turns
                    self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                    return True
                return False
            except ValueError:
                return False

    def get_fen(self):
        with self.lock:
            return self.board.fen()

    def is_game_over(self):
        with self.lock:
            return self.board.is_game_over()

    def result(self):
        with self.lock:
            return self.board.result()

    def get_current_turn(self):
        with self.lock:
            return self.current_turn

    def get_all_clients(self):
        with self.lock:
            return list(self.players.values()) + list(self.spectators)

    def is_full(self):
        with self.lock:
            return len(self.players) >= 2


# Game Manager
class GameManager:
    def __init__(self):
        self.rooms: Dict[str, MultiplayerChessGame] = {}
        self.lock = threading.Lock()

    def get_or_create_room(self, room_id: str) -> MultiplayerChessGame:
        with self.lock:
            if room_id not in self.rooms:
                self.rooms[room_id] = MultiplayerChessGame(room_id)
            return self.rooms[room_id]

    def remove_empty_rooms(self):
        with self.lock:
            empty_rooms = []
            for room_id, game in self.rooms.items():
                has_no_players = len(game.players) == 0
                has_no_spectators = len(game.spectators) == 0
                
                if has_no_players and has_no_spectators:
                    empty_rooms.append(room_id)
            for room_id in empty_rooms:
                del self.rooms[room_id]


game_manager = GameManager()


async def handle_singleplayer(websocket):
    print(f"Singleplayer client connected: {websocket.remote_address[0]}")
    game = SingleplayerChessGame()
    
    try:
        # Send initial board state
        await send_json(websocket, {"command": "fen", "value": game.get_fen()})

        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")

                if command == "move":
                    move_uci = data.get("value")
                    if game.make_move(move_uci):
                        await send_json(websocket, {"command": "fen", "value": game.get_fen()})

                        # Check game over
                        if game.is_game_over():
                            print("Singleplayer game ended")
                            await send_json(websocket, {"command": "gameover", "value": game.result()})

            except json.JSONDecodeError:
                print("Invalid JSON received")

    except websockets.exceptions.ConnectionClosed:
        print("Singleplayer client disconnected")
    finally:
        print("Singleplayer client disconnected")


async def handle_multiplayer(websocket, room_id: str):
    print(f"Multiplayer client connected to room {room_id}: {websocket.remote_address[0]}")
    
    game = game_manager.get_or_create_room(room_id)
    player_color = game.add_player(websocket)
    
    try:
        # Send initial game state to the new player
        await send_json(websocket, {"command": "fen", "value": game.get_fen()})
        await send_json(websocket, {"command": "turn", "value": game.get_current_turn()})

        if player_color:
            await send_json(websocket, {"command": "color", "value": player_color})
            
            # Check if this is the second player joining
            if len(game.players) == 2:
                await broadcast_to_room(game, {"command": "game_ready", "value": "Both players connected! Game starting..."})
            else:
                # First player joined, waiting for second
                await send_json(websocket, {"command": "waiting", "value": "Waiting for another player to join..."})
        else:
            await send_json(websocket, {"command": "spectator", "value": "Game is full, you are spectating"})

        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get("command")

                if command == "move":
                    move_uci = data.get("value")
                    if game.make_move(move_uci, websocket):
                        # Broadcast the new board state to all clients
                        await broadcast_to_room(game, {"command": "fen", "value": game.get_fen()})
                        await broadcast_to_room(game, {"command": "turn", "value": game.get_current_turn()})

                        # Check game over
                        if game.is_game_over():
                            print(f"Multiplayer game in room {room_id} ended")
                            await broadcast_to_room(game, {"command": "gameover", "value": game.result()})
                    else:
                        await send_json(websocket, {"command": "invalid_move", "value": "Invalid move or not your turn"})

            except json.JSONDecodeError:
                print("Invalid JSON received")

    except websockets.exceptions.ConnectionClosed:
        print(f"Multiplayer client disconnected from room {room_id}")
    finally:
        print(f"Multiplayer client disconnected from room {room_id}")
        game.remove_player(websocket)
        if player_color:
            await broadcast_to_room(game, {"command": "player_left", "value": f"{player_color} player left"})
        game_manager.remove_empty_rooms()


async def broadcast_to_room(game: MultiplayerChessGame, message: dict):
    if game.get_all_clients():
        await asyncio.gather(
            *[send_json(client, message) for client in game.get_all_clients()],
            return_exceptions=True
        )


async def handle_connection(websocket):
    try:
        # Wait for the first message to determine game mode
        initial_message = await websocket.recv()
        data = json.loads(initial_message)
        
        mode = data.get("mode")
        
        if mode == "singleplayer":
            await handle_singleplayer(websocket)
        elif mode == "multiplayer":
            room_id = data.get("room_id", "default")
            await handle_multiplayer(websocket, room_id)
        else:
            await send_json(websocket, {"command": "error", "value": "Invalid game mode"})
            
    except json.JSONDecodeError:
        await send_json(websocket, {"command": "error", "value": "Invalid JSON in initial message"})
    except Exception as e:
        print(f"Error handling connection: {e}")


async def send_json(websocket, data):
    try:
        json_string = json.dumps(data)
        await websocket.send(json_string)
    except websockets.exceptions.ConnectionClosed:
        pass  # Client disconnected


async def main():
    ip = "localhost"
    port = 8888
    server = await websockets.serve(handle_connection, ip, port)
    print(f"Chess server started at ws://{ip+":"+str(port)}")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())