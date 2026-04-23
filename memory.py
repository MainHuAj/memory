from qdrant_client import QdrantClient,models
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
from typing import Union
import os
import math
load_dotenv()


qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL") ,
    api_key=os.getenv("QDRANT_API_KEY"),
)



if not qdrant_client.collection_exists("test"):
    qdrant_client.create_collection(
        collection_name="test",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

# create_collection("test")

# print(qdrant_client.get_collections())

model = SentenceTransformer("all-MiniLM-L6-v2")

def store_memory(text : str,user_id:str):
    embedding = model.encode(text)
    duplicate_check = qdrant_client.query_points(
        collection_name="test",
        limit = 1,
        query= embedding.tolist(),
        score_threshold=0.9,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="person",
                    match=models.MatchValue(value=user_id)
                )
            ]
        )
    )
    if duplicate_check.points:
        return

    qdrant_client.upsert(
        collection_name="test",
       points = [PointStruct(
    id=str(uuid.uuid4()),
    payload={"memory": text, "person": user_id, "created": datetime.datetime.now().isoformat()},
    vector=embedding.tolist()
)]
    )

try:
    qdrant_client.create_payload_index(
        collection_name="test",
        field_name="person",
        field_schema=models.PayloadSchemaType.KEYWORD
    )

except Exception as e:
    print("Index creation failed:", e)

# store_memory("I am building a memory layer for LLMs like claude", "aj_124", "test")

  # decays slowly over time

def retrieve_memory(query:str,user_id:str):
    embedding = model.encode(query)

    results = qdrant_client.query_points(
        collection_name = "test",
        query = embedding.tolist(),
        limit = 5,
        score_threshold = 0.5,
        query_filter = models.Filter(
            must =[
                models.FieldCondition(
                    key = "person",
                    match = models.MatchValue(value=user_id)
                )
            ]
        )
    )
    scored_results = []
    for result in results.points:
        days_old = (datetime.now() - datetime.fromisoformat(result.payload["created"])).days
        time_decay = math.exp(-0.01 * days_old)
        importance = result.payload.get("importance", 0.5)
        final_score = result.score * time_decay * importance
        scored_results.append((final_score,result))
    scored_results.sort(key = lambda x : x[0],reverse=True)
    return [r for _,r in scored_results]

# results = retrieve_memory("LLMs", "aj_124", "test")
# print(results)

def delete_memory(user_id : str,memory_id :str):
    results = qdrant_client.retrieve(
        collection_name="test",
        ids= [memory_id],
        with_payload= True
    )
    if not results:
        raise Exception("Memory not found")
    if results[0].payload["person"] != user_id:
        raise Exception("Unauthorized")
    
    qdrant_client.delete(
        collection_name="test",
        points_selector=models.PointIdsList(
            points=[memory_id]
        )
    )

def get_memories(user_id: str, limit: int, offset: Union[int,str]=0):
    points, next_offset = qdrant_client.scroll(
        collection_name="test",
        scroll_filter=models.Filter(must=[
            models.FieldCondition(
                key="person",
                match=models.MatchValue(value=user_id)
            )
        ]),
        with_payload=True,
        limit=limit,
        offset=offset
    )
    
    return points,next_offset
 