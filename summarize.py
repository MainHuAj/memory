from groq import Groq
from dotenv import load_dotenv
import json
load_dotenv()

def extract_facts(conversation: str):
    client = Groq()
    prompt = f'''You are pro in summarizing chats in one line and also extracting facts from a conversation between an LLM and its user , you will be given the whole conversation you have to return a full JSON without any preamble or anything else , there is a parameter called as importance in the json , it should reflect how significant the conversation was, between 0 and 1, i am giving you an example how the JSON should look:
   json: {{
  "summary": "one sentence overview",
  "facts": [
    "AJ is using Qdrant as vector database",
    "AJ chose all-MiniLM-L6-v2 for embeddings",
    "AJ is building FastAPI backend"
  ],
  "category": "technical",
  "importance": 0.8
}}
     conversation:{conversation}'''
    completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ],
    temperature=0.8,
    max_completion_tokens=8192
)
    try:
        result = json.loads(completion.choices[0].message.content)
        return result
    except Exception as e:
        print(e)
        return {"message":"Error in parsing json string","details":e}
    


test_conversation = """
User: I am building a memory layer for LLMs
Assistant: That's a great idea, tell me more
User: I want to use Qdrant as the vector database and FastAPI as the backend
Assistant: Good choices, what embedding model are you planning to use?
User: I will use all-MiniLM-L6-v2
"""

# print(extract_facts(test_conversation))