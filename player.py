import argparse
import asyncio
import json
import httpx
import redis.asyncio as aioredis
import websockets
import os

redisPubSubKey = "ttt_game_state_changed"

# FastAPI base URL
BASE_URL = "http://localhost:8000"
 
# CLI argument parsing
parser = argparse.ArgumentParser(description="Tic Tac Toe Game Client")
parser.add_argument(
    "--player", choices=["white", "black"], required=True, help="Which player are you?"
)
parser.add_argument(
    "--reset", action="store_true", help="Reset the board before starting the game."
)
parser.add_argument("--team", required=True, help="Your team number (used as Redis DB number)")
args = parser.parse_args()

i_am_playing = args.player
team_number = int(args.team)
team_number_str = f"{team_number:02d}"
WS_URL = f"ws://ai.thewcl.com:87{team_number_str}"
print(f"Connecting to WebSocket server at {WS_URL}")

# Redis Pub/Sub setup
r = aioredis.Redis(
    host="ai.thewcl.com", port=6379, db=team_number, password=os.getenv("WCL_REDIS_PASSWORD"), decode_responses=True
)
redisPubSubKey = "ttt_game_state_changed"

# FastAPI base URL
BASE_URL = "http://localhost:8000"


async def reset_board():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/reset")
        print("Game reset:", response.json())


async def get_board():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/state")
        return response.json()


async def post_move(player, from_index, to_index):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/move", json={
                "player": player,
                "from_index": from_index,
                "to_index": to_index
            }
        )
        return response



async def send_positions_over_websocket(websocket):
    board = await get_board()
    positions = board.get("positions")
    if isinstance(positions, list) and len(positions) == 64:
        await websocket.send(json.dumps({"positions": positions}))


async def handle_board_state(websocket):
    # Get the current board state (this fetches the FEN and other info from the backend)
    board = await get_board()

    print(json.dumps(board, indent=2))  # Debugging: print current board state

    if board["state"] != "is_playing":
        print("Game over.")
        return

    if board["player_turn"] == i_am_playing:
        while True:  # Loop until a valid move is entered
            try:
                # Prompt for the 'from' and 'to' squares
                from_index = int(input("Your turn! Move FROM (0-63): ").strip())
                to_index = int(input("Move TO (0-63): ").strip())
                
                # Ensure the input indices are valid
                if from_index < 0 or from_index >= 64 or to_index < 0 or to_index >= 64:
                    print("Invalid square indices! Please enter values between 0 and 63.")
                    continue

                # Send the move request to the FastAPI backend for validation
                response = await post_move(i_am_playing, from_index, to_index)

                # Check if the move was successful
                if response.status_code == 200:
                    print(response.json()["message"])
                    await r.publish(redisPubSubKey, "update")
                    break  # Exit the loop when a valid move is made
                else:
                    print("Error:", response.json()["detail"])

            except ValueError:
                print("Invalid input. Please enter valid integers for from_index and to_index.")
            except Exception as e:
                print(f"Error: {e}")
    
    else:
        print("Waiting for the opponent...")

    # Send the updated board state after each move
    await send_positions_over_websocket(websocket)



async def listen_for_updates(websocket):
    pubsub = r.pubsub()
    await pubsub.subscribe(redisPubSubKey)
    print(f"Subscribed to {redisPubSubKey}. Waiting for updates...\n")
    await handle_board_state(websocket)

    async for message in pubsub.listen():
        if message["type"] == "message":
            print("\nReceived update!")
            await handle_board_state(websocket)


async def main():
    if args.reset:
        await reset_board()
        return

    async with websockets.connect(WS_URL) as websocket:
        await listen_for_updates(websocket)


'''
if __name__ =="__main__":
    empyt_board = ["" for _ in range(64)]
    render_board(empyt_board))
'''

if __name__ == "__main__":
    asyncio.run(main())