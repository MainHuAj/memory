from fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("RAILWAY_URL")

mcp = FastMCP("Memory Layer")

@mcp.tool()
def store_memory(conversation: str, user_id: str):
    "Stores conversation in memory"
    response = requests.post(
        f"{BASE_URL}/store",
        json={"text": conversation, "user_id": user_id}
    )
    return response.json()

@mcp.tool()
def retrieve_memory(query: str, user_id: str):
    "Retrieves relevant memories related to the query "
    response = requests.post(
        f"{BASE_URL}/retrieve",
        json={"query":query,"user_id":user_id}
    )
    return response.json()

if __name__ == "__main__":
    mcp.run()