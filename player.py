import argparse
import asyncio
import json
import httpx
import redis.asyncio as aioredis
import websockets
import os
import ipdb

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

parser.add_argument("--ai", action="store_true", help="Play against AI")
args = parser.parse_args()

i_am_playing = args.player
ai = args.ai
team_number = int(args.team)
WS_URL = f"ws://ai.thewcl.com:8702"
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
                if ai:
                    #call ai
                    from_index, to_index = await get_ai_move()
                    print(f"AI move: {from_index} -> {to_index}")
                else:
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
    if ai:
        await post_ai_move(from_index, to_index)

## AI

async def get_ai_move():
    board = await get_board()  # make sure this is inside an `async def`
    positions = board["positions"]
    player_turn = board["player_turn"]

    data = {
        "model": "gpt-4.1-nano",
        "system_prompt": "You are a expert chess player",
        "user_prompt": f"The current board state is: {positions}. Its a 64 square board, from top-left to bottom-right. 8x8 chess board. bR is the black Rook, wR is the white Rook, bK is the black King, wK is the white King, bQ is the black Queen, wQ is the white Queen, bB is the black Bishop, wB is the white Bishop, bN is the black Knight, wN is the white Knight, bP is the black Pawn, wP is the white Pawn. It's {player_turn}'s turn and you are {i_am_playing}. Make the next best move. Respond with a JSON object like this: {{ \"from_index\": 12, \"to_index\": 28 }}"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer stu-Mahdi-cea6af21c6be379adb17d8170a188934"
    }

    # Send the request
    response = httpx.post("http://ai.thewcl.com:6502/chat?json=true", json=data, headers=headers)
    data = response.json()
    output = data.get("output")
    content = output[0].get("content")
    text = content[0].get("text")
    json_parsed = json.loads(text)
    from_index = json_parsed.get("from_index")
    to_index = json_parsed.get("to_index")
    return from_index, to_index

async def post_ai_move(from_index, to_index):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/move", json={
                "player": i_am_playing,
                "from_index": from_index,
                "to_index": to_index
            }
        )
        return response
'''
if __name__ =="__main__":
    empyt_board = ["" for _ in range(64)]
    render_board(empyt_board))
'''

if __name__ == "__main__":
    asyncio.run(main())