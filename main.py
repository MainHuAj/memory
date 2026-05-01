
from fastapi import FastAPI,status,HTTPException
from pydantic import BaseModel,Field
from memory import store_memory,retrieve_memory,delete_memory,get_memories,qdrant_client
from summarize import extract_facts
from typing import Union
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import get_current_user,supabase
from fastapi.middleware.cors import CORSMiddleware
security = HTTPBearer()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class StoreRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    
   
class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)

@app.post("/store")
def store(request:StoreRequest,credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    try:
        user_id = get_current_user(credentials.credentials)
        result = extract_facts(request.text)
        print("RESULT:", result)
        importance = result['importance']
        print("IMPORTANCE:", importance)
        for fact in result["facts"]:
            store_memory(fact,importance,user_id)
        store_memory(result["summary"],importance,user_id)
        return {"message": "memory stored successfully"}
    except Exception as e:
       print(e)
       raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail="Something went wrong"
       )
        





@app.post("/retrieve")
def retrieve(request:RetrieveRequest,credentials: HTTPAuthorizationCredentials = Depends(security)):
   
    try:
        user_id = get_current_user(credentials.credentials)
        retrieved_memory = retrieve_memory(request.query,user_id)
        return [r.payload['memory'] for r in retrieved_memory]
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
        )

@app.delete("/delete/{memory_id}")
def delete(memory_id:str,credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_id = get_current_user(credentials.credentials)
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
            

@app.get("/memories")
def memories(limit:int = 10,offset :Union[int,str] = 0,credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_id = get_current_user(credentials.credentials)
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



class SignUpRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/signup")
def signup(request:SignUpRequest):
    try:
        response = supabase.auth.sign_up({"email": request.email, "password": request.password})
        return {"user":response.user.email,"session":response.session}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail= "Error Signing Up"
        )

@app.post("/login")
def login(request:LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({"email": request.email, "password": request.password})
        return {"user":response.user.email,"session":response.session}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or Password invalid"
        )