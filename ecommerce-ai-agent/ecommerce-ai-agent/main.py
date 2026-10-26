from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.agent import chat
from app.models import ChatRequest, ChatResponse

app = FastAPI(title="TechZone AI Support Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    reply = await chat(request.message)
    return ChatResponse(
        reply=reply,
        intent="classified",
        thread_id=request.thread_id
    )


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "TechZone AI v1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
