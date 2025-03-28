from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from knowledge_base import ThinkScriptKnowledgeBase

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    content: str
    sources: List[dict]

# Initialize knowledge base
kb = ThinkScriptKnowledgeBase()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get the last user message
        user_message = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
        if not user_message:
            raise HTTPException(status_code=400, detail="No user message found")

        # Get relevant nodes and generate response
        relevant_nodes = kb.find_relevant_nodes(user_message)
        response = kb.generate_response(user_message, relevant_nodes)

        # Format sources
        sources = [
            {
                "name": node["name"],
                "content": node["content"]
            }
            for node in relevant_nodes
        ]

        return ChatResponse(content=response, sources=sources)

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 