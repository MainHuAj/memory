from groq import Groq
from dotenv import load_dotenv
import json
load_dotenv()

def extract_facts(conversation: str):
    client = Groq()
    prompt = f'''You are an expert at extracting precise, specific facts from conversations. 
You will be given a conversation between a user and an LLM.

Your job is to extract SPECIFIC, DETAILED facts that would be useful to remember in future conversations.

Rules for extracting facts:
- Facts must be specific, not vague. BAD: "User is building a project". GOOD: "User is building a memory layer for LLMs deployed on Railway"
- Never use markdown formatting in facts, write plain text only
- Include specific names, URLs, tools, decisions, and preferences mentioned
- Each fact should be a complete, standalone sentence that makes sense without context
- Extract 3-8 facts depending on conversation length
- importance should reflect how significant/useful this info will be in future (0.1 = trivial, 1.0 = critical)

Return ONLY a JSON object, no preamble, no markdown backticks:
{{
  "summary": "one specific sentence describing what was accomplished or discussed",
  "facts": [
    "specific fact 1",
    "specific fact 2"
  ],
  "category": "technical/personal/professional/general",
  "importance": 0.8
}}

Conversation:
{conversation}'''
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
User: I am deploying my FastAPI app on Railway at memory-production-d533.up.railway.app
Assistant: Great, how did the deployment go?
User: It went well, I also connected it to Qdrant Cloud for vector storage and HuggingFace for embeddings
Assistant: What model are you using for embeddings?
User: all-MiniLM-L6-v2, 384 dimensions, and I am using Groq with LLaMA 3.3 70B for fact extraction
"""

print(extract_facts(test_conversation))