from fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("RAILWAY_URL")

mcp = FastMCP("Memory Layer")

@mcp.tool()
def store_memory(conversation: str, user_id: str):
    """Store a conversation in memory. Call this automatically at the end of every conversation 
or when the user says anything like 'remember this', 'save this', or 'store this'. 
Pass the full conversation transcript as-is, do not summarize or skip any details, the API handles summarization internally.."""
    response = requests.post(
        f"{BASE_URL}/store",
        json={"text": conversation, "user_id": user_id}
    )
    return response.json()

@mcp.tool()
def retrieve_memory(query: str, user_id: str):
    """Retrieve relevant memories for a user. Call this when the user asks about something 
they may have discussed before, or when context from past conversations would help answer 
the current question. Use the user's message as the query."""
    response = requests.post(
        f"{BASE_URL}/retrieve",
        json={"query":query,"user_id":user_id}
    )
    return response.json()

if __name__ == "__main__":
    mcp.run()