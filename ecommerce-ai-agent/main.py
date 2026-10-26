import os, jwt, uvicorn
from fastapi import FastAPI, HTTPException, Security, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.agent import chat

load_dotenv()
ENV = os.getenv("ENVIRONMENT", "production")
JWT_SECRET = os.getenv("JWT_SECRET")

app = FastAPI(docs_url=None if ENV == "production" else "/docs", redoc_url=None if ENV == "production" else "/redoc")

# Rate Limiter (10 req/min)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8501"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Auth Security
security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid/Expired Token")

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

# 🔑 Endpoint for Streamlit to get a mock token (For Testing UI)
@app.get("/api/v1/auth/mock-token")
async def get_mock_token():
    token = jwt.encode({"user_id": "user_12345"}, JWT_SECRET, algorithm="HS256")
    return {"access_token": token}

@app.post("/api/v1/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, body: ChatRequest, user_id: str = Depends(verify_jwt)):
    try:
        # Secure isolation: combine user_id from token with frontend session_id
        secure_thread_id = f"{user_id}_{body.session_id}"
        reply = await chat(user_input=body.message, thread_id=secure_thread_id)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main.py:app", host="0.0.0.0", port=8000)