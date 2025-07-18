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

 
# Build the WebSocket URL dynamically
WEBSOCKET_URL = f"ws://ai.thewcl.com:8702"


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def format_cell(value, index):
    return value if value else f"{index:02d}"



def render_board(positions):
    assert len(positions) == 64, "Board must have 64 positions."

    def format_square(value, index):
        return value if value else f"{index:02d}"

    for row in range(8):
        line = " | ".join(format_square(positions[row * 8 + col], row * 8 + col) for col in range(8))
        print(" " + line)
        if row < 7:
            print("-" * (len(line) + 1))



async def listen_for_updates():
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f"Connected to {WEBSOCKET_URL}")
        async for message in ws:
            try:
                data = json.loads(message)
                positions = data.get("positions")
                if isinstance(positions, list) and len(positions) == 64:
                    clear_terminal()
                    render_board(positions)
                else:
                    print("Invalid board data received.")
            except json.JSONDecodeError:
                print("Received non-JSON message.")



if __name__ == "__main__":
    
    render_board(["" for _ in range(64)])
    asyncio.run(listen_for_updates())