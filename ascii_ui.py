import asyncio
import websockets
import json
import os
import argparse

# Parse required --team argument
parser = argparse.ArgumentParser(description="ASCII UI for Tic Tac Toe")
parser.add_argument("--team", required=True, help="Your team number (used as WebSocket port)")
args = parser.parse_args()
team_number = int(args.team)
team_number_str = f"{team_number:02d}"

# Build the WebSocket URL dynamically
WEBSOCKET_URL = f"ws://ai.thewcl.com:87{team_number_str}"


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def format_cell(value, index):
    upper = str(value).upper()
    return upper if upper in ["white", "black"] else str(index)


def render_chess_board(positions: list[str]):
    PIECE_SYMBOLS = {
        "white_pawn": "WP",  "white_rook": "WR",  "white_knight": "WN", "white_bishop": "WB",
        "white_queen": "WQ", "white_king": "WK",
        "black_pawn": "BP",  "black_rook": "BR",  "black_knight": "BN", "black_bishop": "BB",
        "black_queen": "BQ", "black_king": "BK",
    }

    def format_cell(piece):
        return PIECE_SYMBOLS.get(piece, ".")

    columns = "A B C D E F G H".split()
    print("    " + "  ".join(columns))
    print("  +" + "---+" * 8)

    for row in range(8):
        row_str = f"{8 - row} |"
        for col in range(8):
            idx = row * 8 + col
            piece = format_cell(positions[idx])
            row_str += f" {piece} |"
        print(row_str)
        print("  +" + "---+" * 8)

async def listen_for_updates():
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f"Connected to {WEBSOCKET_URL}")
        async for message in ws:
            try:
                data = json.loads(message)
                positions = data.get("positions")
                if isinstance(positions, list) and len(positions) == 64:
                    clear_terminal()
                    render_chess_board(positions)
                else:
                    print("Invalid board data received.")
            except json.JSONDecodeError:
                print("Received non-JSON message.")


if __name__ == "__main__":
    positions = [""] * 64
    positions[60] = "white_king"   # e1
    positions[4] = "black_king"    # e8

    render_chess_board(positions)

    asyncio.run(listen_for_updates())