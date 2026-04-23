
from fastapi import FastAPI,status,HTTPException
from pydantic import BaseModel,Field
from memory import store_memory,retrieve_memory,delete_memory,get_memories,qdrant_client
from summarize import extract_facts
from typing import Union


app = FastAPI()

class StoreRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    user_id: str = Field(..., min_length=3, max_length=50)
   
class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    user_id: str = Field(..., min_length=3, max_length=50)

@app.post("/store")
def store(request:StoreRequest):

    try:
        result = extract_facts(request.text)
        for fact in result["facts"]:
            store_memory(fact,request.user_id)
        store_memory(result["summary"],request.user_id)
        return {"message": "memory stored successfully"}
    except Exception as e:
       print(e)
       raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail="Something went wrong"
       )
        





@app.post("/retrieve")
def retrieve(request:RetrieveRequest):
    try:
        retrieved_memory = retrieve_memory(request.query,request.user_id)
        return [r.payload['memory'] for r in retrieved_memory]
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
        )

@app.delete("/delete/{memory_id}")
def delete(user_id:str,memory_id:str):
    try:
        delete_memory(user_id,memory_id)
        return {"message":"memory deleted successfully"}
    except Exception as e:
        print(e)
        if "memory not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Memory not found")
        elif "unauthorized" in str(e).lower():
            raise HTTPException(status_code=403, detail="Unauthorized")
        else:
            raise HTTPException(status_code=500, detail="Something went wrong")
            

@app.get("/memories/{user_id}")
def memories(user_id :str,limit:int = 10,offset :Union[int,str] = 0):
    try:
        points , next_offset = get_memories(user_id,limit,offset)
        return {
        "memories": [{"memory": p.payload["memory"], "id": p.id} for p in points],
        "next_offset": next_offset
    }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch memories"
        )


@app.get("/health")
def health():
    try:
        qdrant_client.get_collections()
        return {"status": "ok"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

