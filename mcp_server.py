from fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("RAILWAY_URL")

mcp = FastMCP("Memory Layer")

EMAIL = os.getenv("MEMORY_EMAIL")
PASSWORD = os.getenv("MEMORY_PASSWORD")

def get_token():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    return response.json()["session"]["access_token"]

@mcp.tool()
def store_memory(conversation: str):
    """Store a conversation in memory. Call this automatically at the end of every conversation 
or when the user says anything like 'remember this', 'save this', or 'store this'. 
Pass the full conversation transcript as-is, do not summarize or skip any details, the API handles summarization internally.."""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/store",
        json={"text": conversation},
        headers=headers
    )
    return response.json()

@mcp.tool()
def retrieve_memory(query: str):
    """Retrieve relevant memories for a user. Call this when the user asks about something 
they may have discussed before, or when context from past conversations would help answer 
the current question. Use the user's message as the query."""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/retrieve",
        json={"query":query},
        headers=headers
    )
    return response.json()

if __name__ == "__main__":
    mcp.run()