from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os

app = FastAPI(title="对话机器人后端服务", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None

class DocumentRequest(BaseModel):
    file_path: str
    file_type: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

def get_session_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"{session_id}.json")

def load_session(session_id: str) -> List[Dict]:
    path = get_session_path(session_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_session(session_id: str, messages: List[Dict]):
    path = get_session_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def generate_session_id(user_id: str) -> str:
    import uuid
    return f"{user_id}_{uuid.uuid4().hex[:8]}"

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.session_id:
        request.session_id = generate_session_id(request.user_id)
    
    messages = load_session(request.session_id)
    messages.append({"role": "user", "content": request.message})
    
    from ai.rag import RAGSystem
    rag = RAGSystem()
    reply, sources, confidence = rag.query(request.message)
    
    messages.append({"role": "assistant", "content": reply})
    save_session(request.session_id, messages)
    
    return ChatResponse(
        session_id=request.session_id,
        reply=reply,
        sources=sources,
        confidence=confidence
    )

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    messages = load_session(session_id)
    return {"session_id": session_id, "messages": messages}

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    path = get_session_path(session_id)
    if os.path.exists(path):
        os.remove(path)
        return {"message": "Session deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/api/documents/load")
async def load_document(request: DocumentRequest):
    from ai.document_loader import DocumentLoader
    loader = DocumentLoader()
    
    try:
        docs = loader.load(request.file_path, request.file_type)
        from ai.rag import RAGSystem
        rag = RAGSystem()
        rag.add_documents(docs)
        return {"message": f"Successfully loaded {len(docs)} documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search(request: SearchRequest):
    from ai.rag import RAGSystem
    rag = RAGSystem()
    results = rag.search(request.query, request.top_k)
    return {"results": results}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "conversation-robot-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)