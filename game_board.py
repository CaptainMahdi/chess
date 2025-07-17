from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dataclasses import dataclass, field, asdict
import redis
from redis.commands.json.path import Path
import json
import ipdb
import chess



r = redis.Redis(host="ai.thewcl.com", port=6379, db=0, password="atmega328")
REDIS_KEY = "tic_tac_toe:game_state"

# ----------------------------
# Data Model
# Starter class for your game board. Rename and modify for your own game.
# ----------------------------
 

@dataclass
class ChessBoard:
    state: str = "is_playing"  # is_playing, has_winner, has_draw
    player_turn: str = "white"
    positions: list[str] = field(default_factory=lambda: [""] * 64)
    fen: str = chess.STARTING_FEN  # saved FEN string

    def get_board(self):
        return chess.Board(self.fen)
    
    def render_board_list(self, board: chess.Board) -> list[str]:
        squares = []
    
        # Loop through all 64 squares
        for i in range(56, 64):  # 8th row (index 56-63)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())  # 'wP' for white pawn, 'bK' for black king
            else:
                squares.append("")  # Empty square, use "" for no piece

        for i in range(48, 56):  # 7th row (index 48-55)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        for i in range(40, 48):  # 6th row (index 40-47)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        for i in range(32, 40):  # 5th row (index 32-39)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        for i in range(24, 32):  # 4th row (index 24-31)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        for i in range(16, 24):  # 3rd row (index 16-23)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        for i in range(8, 16):  # 2nd row (index 8-15)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        for i in range(0, 8):  # 1st row (index 0-7)
            piece = board.piece_at(i)
            if piece:
                if piece.color == chess.WHITE:
                    color = "w"
                else:
                    color = "b"
                squares.append(color + piece.symbol().upper())
            else:
                squares.append("")

        return squares



    def is_my_turn(self, player: str) -> bool:
        return self.state == "is_playing" and player == self.player_turn

    def make_move(self, player: str, from_index: int, to_index: int) -> dict:
        board = chess.Board(self.fen)

        # Check if game is already over
        if board.is_game_over():
            return {"success": False, "message": "Game is over. Please reset."}

        # Convert 0-63 indices to algebraic notation
        from_square = chess.square(from_index % 8, 7 - from_index // 8)
        to_square = chess.square(to_index % 8, 7 - to_index // 8)

        move = chess.Move(from_square, to_square)

        # Validate the move
        if move not in board.legal_moves:
            return {"success": False, "message": "Illegal move."}

        # Validate it's the right player's turn
        expected_color = chess.WHITE if player == "white" else chess.BLACK
        if board.turn != expected_color:
            return {"success": False, "message": f"It is not {player}'s turn."}

        # Apply the move to the board
        print(board)
        board.push(move)
        print(board)

        # Update state after the move
        self.fen = board.fen()  # Save the updated FEN string
        self.player_turn = "white" if board.turn == chess.WHITE else "black"
        self.state = self.get_state(board)  # Check if it's a draw, checkmate, etc.

        # Update positions list based on the new board
        print(self.positions)
        self.positions = self.render_board_list(board)
        print(self.positions)

        # Save updated state to Redis
        self.save_to_redis()

        return {
            "success": True,
            "message": "Move accepted.",
            "fen": self.fen,
            "state": self.state,
            "player_turn": self.player_turn,
            "positions": self.positions
        }

    def get_state(self, board: chess.Board) -> str:
        if board.is_checkmate():
            return "has_winner"
        elif board.is_stalemate() or board.is_insufficient_material():
            return "has_draw"
        return "is_playing"

    def check_winner(self) -> str | None:
        wins = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]
        for a, b, c in wins:
            if (
                self.positions[a]
                and self.positions[a] == self.positions[b] == self.positions[c]
            ):
                return self.positions[a]
        return None

    def check_draw(self) -> bool:
        return (
            all(cell != "" for cell in self.positions) and self.check_winner() is None
        )

    def switch_turn(self):
        self.player_turn = "white" if self.player_turn == "black" else "black"

    def reset(self):
        self.state = "is_playing"
        self.player_turn = "white"
        self.fen = chess.STARTING_FEN
        self.setup_starting_position()
        self.save_to_redis()

    def save_to_redis(self):
        r.json().set(REDIS_KEY, Path.root_path(), self.to_dict())

    @classmethod
    def load_from_redis(cls):
        data = r.json().get(REDIS_KEY)
        return cls(**data) if data else cls()

    def to_dict(self):
        return asdict(self)

    def serialize(self):
        return json.dumps(self.to_dict())
    
    def setup_starting_position(self):
        self.positions = [""] * 64

        # Setup pawns
        for i in range(8, 16):
            self.positions[i] = "bP"
        for i in range(48, 56):
            self.positions[i] = "wP"

        # Setup rooks
        self.positions[0] = self.positions[7] = "bR"
        self.positions[56] = self.positions[63] = "wR"

        # Setup knights
        self.positions[1] = self.positions[6] = "bN"
        self.positions[57] = self.positions[62] = "wN"

        # Setup bishops
        self.positions[2] = self.positions[5] = "bB"
        self.positions[58] = self.positions[61] = "wB"

        # Setup queens
        self.positions[3] = "bQ"
        self.positions[59] = "wQ"

        # Setup kings
        self.positions[4] = "bK"
        self.positions[60] = "wK"



# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI()


class MoveRequest(BaseModel):
    player: str
    from_index: int
    to_index: int



@app.get("/state")
def get_state():
    board = ChessBoard.load_from_redis()
    return board.to_dict()


@app.post("/move")
def post_move(req: MoveRequest):
    board = ChessBoard.load_from_redis()
    result = board.make_move(req.player, req.from_index, req.to_index)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/reset")
def post_reset():
    board = ChessBoard()
    board.reset()
    return {"message": "Game reset", "board": board.to_dict()}