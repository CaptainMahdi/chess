from dataclasses import dataclass
import json




@dataclass
class piece:
    name: str
    position: str

    def take(self):
        return piece(self.name, self.position)


print(json.dumps(piece("Black pawn", "e5").take()))