from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from knowledge_base import ThinkScriptKnowledgeBase
import json
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize knowledge base
kb = ThinkScriptKnowledgeBase()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-3.5-turbo"  # Default to GPT-3.5

@app.get("/")
async def root():
    return {"message": "ThinkScript API is running"}

async def stream_response(messages, model: str):
    try:
        # Convert messages to the format expected by the API
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Add system message
        formatted_messages.insert(0, {
            "role": "system",
            "content": """You are a helpful assistant that answers questions about ThinkScript programming language.
                         Your responses should be:
                         1. Clear and concise
                         2. Include code examples when relevant
                         3. Explain the key concepts
                         4. Provide step-by-step instructions when needed
                         5. Include any important warnings or considerations
                         
                         If you find multiple relevant pieces of information, combine them to provide a comprehensive answer.
                         If you're not sure about something, say so rather than making assumptions.
                         Always format code examples with proper indentation and comments."""
        })
        
        # Get streaming response
        response = kb.generate_response(
            messages=formatted_messages,
            stream=True,
            temperature=0.7,
            max_tokens=1000,
            model=model
        )
        
        # Stream the response
        if model.startswith('claude'):
            async for chunk in response:
                if chunk.type == 'content_block_delta':
                    yield f"data: {json.dumps({'content': chunk.delta.text})}\n\n"
        else:
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
                
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_response(request.messages, request.model),
        media_type="text/event-stream"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 