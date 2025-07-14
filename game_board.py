from dataclasses import dataclass, field, asdict
import redis
from redis.commands.json.path import Path
import json

r = redis.Redis(host="ai.thewcl.com", port=6379, db=2, password="atmega328")
REDIS_KEY = "chess:game_state"

# ----------------------------
# Data Model
# Starter class for your game board. Rename and modify for your own game.
# ----------------------------


@dataclass
class ChessBoard:
    state: str = "is_playing"  # is_playing, has_winner, has_draw
    player_turn: str = "white"
    positions: list[str] = field(default_factory=lambda: [""] * 64)

    def is_my_turn(self, player: str) -> bool:
        return self.state == "is_playing" and player == self.player_turn

    def make_move(self, player: str, index: int) -> dict:
        if self.state != "is_playing":
            return {"success": False, "message": "Game is over. Please reset."}

        if not self.is_my_turn(player):
            return {"success": False, "message": f"It is not {player}'s turn."}

        if not 0 <= index < 64:
            return {
                "success": False,
                "message": "Invalid index. Must be between 0 and 63.",
            }

        if self.positions[index]:
            return {"success": False, "message": "That position is already taken."}

        self.positions[index] = player

        if self.check_winner():
            self.state = "has_winner"
        elif self.check_draw():
            self.state = "has_draw"
        else:
            self.switch_turn()

        self.save_to_redis()
        return {"success": True, "message": "Move accepted.", "board": self.to_dict()}

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
        self.positions = [""] * 64
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

