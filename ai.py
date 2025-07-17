
import httpx
import json

# Request payload and headers (same as before)
data = {
    "model": "gpt-4.1-nano",
    "system_prompt": "You are a helpful assistant",
    "user_prompt": "give me my name back in json, with firstname and lastname properties. My full name is Mahdi Hteit"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer stu-Mahdi-cea6af21c6be379adb17d8170a188934"
}

# Send the request
response = httpx.post("http://ai.thewcl.com:6502/chat?json=true", json=data, headers=headers)

# Step 1: Parse the first-level JSON
data = response.json()
output = data.get("output")
content = output[0].get("content")
text = content[0].get("text")
json_parsed = json.loads(text)
firstname = json_parsed.get("firstname")
lastname = json_parsed.get("lastname") 
print(firstname)
print(lastname)
'''
response_data = response.json()
output_text = response_data.get("output")


# Step 2: Parse the stringified JSON inside "output"
print("Raw response data:", response_data)
print("output field:", response_data.get("output"))
print("output type:", type(response_data.get("output")))
try:
    name_data = json.loads(output_text)
    firstname = name_data.get("firstname")
    lastname = name_data.get("lastname")

    print("Type of output_text:", type(output_text))
    print("Value:", output_text)

except json.JSONDecodeError:
    print("Failed to decode nested JSON:", output_text)
    

'''

data = {
    "model": "gpt-4.1-nano",
    "system_prompt": "You are a expert chess player",
    "user_prompt": f"Here is the board state as a list of 64 squares from top-left to bottom-right: [...]. It's white's turn. What is the best move? Give the move as JSON: { \"from_index\": x, \"to_index\": y }"
}
# Fetch current board
board = await get_board()  # make sure this is inside an `async def`
positions = board["positions"]
player_turn = board["player_turn"]

prompt_text = f"""
You are an expert chess player. The current board state is:

{positions}

It's {player_turn}'s turn.
Respond with a JSON object like this: {{ "from_index": 12, "to_index": 28 }}
"""


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
firstname = json_parsed.get("firstname")
lastname = json_parsed.get("lastname") 
print(firstname)
print(lastname)

    data = response.json()
    output = data.get("output")
    content = output[0].get("content")
    text = content[0].get("text")
    json_parsed = json.loads(text)
    from_index = json_parsed.get("from_index")
    to_index = json_parsed.get("to_index")
    return from_index, to_index
