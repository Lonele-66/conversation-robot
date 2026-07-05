from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os
import uuid

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
    answer_format: Optional[str] = "markdown"

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None
    intent: Optional[str] = None

class DocumentRequest(BaseModel):
    file_path: str
    file_type: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

class SensitiveWordRequest(BaseModel):
    word: str

class ConversationRule(BaseModel):
    rule_id: Optional[str] = None
    name: str
    description: str
    condition: str
    action: str
    enabled: bool = True

SESSION_DIR = "sessions"
UPLOAD_DIR = "uploads"
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    return f"{user_id}_{uuid.uuid4().hex[:8]}"

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from ai.sensitive_filter import SensitiveFilter
    from ai.intent_recognizer import IntentRecognizer
    from ai.question_rewriter import QuestionRewriter
    from ai.answer_formatter import AnswerFormatter
    from ai.rag import RAGSystem
    
    filter = SensitiveFilter()
    has_sensitive, found_words = filter.check(request.message)
    
    if has_sensitive:
        return ChatResponse(
            session_id=request.session_id or generate_session_id(request.user_id),
            reply="您的消息包含敏感内容，请重新输入。",
            sources=[],
            confidence=0.0,
            intent="filtered"
        )
    
    if not request.session_id:
        request.session_id = generate_session_id(request.user_id)
    
    messages = load_session(request.session_id)
    messages.append({"role": "user", "content": request.message})
    
    intent_recognizer = IntentRecognizer()
    intent_result = intent_recognizer.recognize(request.message)
    
    rewriter = QuestionRewriter()
    rewritten_question = rewriter.rewrite(request.message)
    
    rag = RAGSystem()
    reply, sources, confidence = rag.query(rewritten_question)
    
    formatter = AnswerFormatter()
    formatted_reply = formatter.format(reply, request.answer_format, sources)
    
    messages.append({"role": "assistant", "content": formatted_reply})
    save_session(request.session_id, messages)
    
    return ChatResponse(
        session_id=request.session_id,
        reply=formatted_reply,
        sources=sources,
        confidence=confidence,
        intent=intent_result["intent"]
    )

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    from ai.document_loader import DocumentLoader
    from ai.rag import RAGSystem
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["txt", "pdf", "docx"]:
        raise HTTPException(status_code=400, detail="不支持的文件格式，请上传 txt、pdf 或 docx 文件")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    try:
        loader = DocumentLoader()
        docs = loader.load(file_path, file_ext)
        
        rag = RAGSystem()
        rag.add_documents(docs)
        
        return {"message": f"成功加载 {len(docs)} 个文档片段", "filename": file.filename}
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/load")
async def load_document(request: DocumentRequest):
    from ai.document_loader import DocumentLoader
    from ai.rag import RAGSystem
    
    loader = DocumentLoader()
    
    try:
        docs = loader.load(request.file_path, request.file_type)
        rag = RAGSystem()
        rag.add_documents(docs)
        return {"message": f"成功加载 {len(docs)} 个文档"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search(request: SearchRequest):
    from ai.rag import RAGSystem
    rag = RAGSystem()
    results = rag.search(request.query, request.top_k)
    return {"results": results}

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    messages = load_session(session_id)
    return {"session_id": session_id, "messages": messages}

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    path = get_session_path(session_id)
    if os.path.exists(path):
        os.remove(path)
        return {"message": "会话已成功删除"}
    raise HTTPException(status_code=404, detail="会话不存在")

@app.get("/api/sessions")
async def list_sessions():
    sessions = []
    for filename in os.listdir(SESSION_DIR):
        if filename.endswith(".json"):
            session_id = filename[:-5]
            sessions.append(session_id)
    return {"sessions": sessions}

@app.get("/api/sensitive-words")
async def get_sensitive_words():
    from ai.sensitive_filter import SensitiveFilter
    filter = SensitiveFilter()
    return {"words": filter.get_all_words()}

@app.post("/api/sensitive-words")
async def add_sensitive_word(request: SensitiveWordRequest):
    from ai.sensitive_filter import SensitiveFilter
    filter = SensitiveFilter()
    filter.add_sensitive_word(request.word)
    return {"message": f"已添加敏感词: {request.word}"}

@app.delete("/api/sensitive-words/{word}")
async def remove_sensitive_word(word: str):
    from ai.sensitive_filter import SensitiveFilter
    filter = SensitiveFilter()
    filter.remove_sensitive_word(word)
    return {"message": f"已删除敏感词: {word}"}

@app.get("/api/intents")
async def get_intents():
    from ai.intent_recognizer import IntentRecognizer
    recognizer = IntentRecognizer()
    return {"intents": recognizer.get_intents()}

@app.get("/api/formats")
async def get_formats():
    from ai.answer_formatter import AnswerFormatter
    formatter = AnswerFormatter()
    return {"formats": formatter.get_available_formats()}

@app.get("/api/rules")
async def get_rules():
    rules_file = os.path.join(os.path.dirname(__file__), "../data/rules.json")
    if os.path.exists(rules_file):
        with open(rules_file, "r", encoding="utf-8") as f:
            return {"rules": json.load(f)}
    return {"rules": []}

@app.post("/api/rules")
async def add_rule(request: ConversationRule):
    rules_file = os.path.join(os.path.dirname(__file__), "../data/rules.json")
    os.makedirs(os.path.dirname(rules_file), exist_ok=True)
    
    rules = []
    if os.path.exists(rules_file):
        with open(rules_file, "r", encoding="utf-8") as f:
            rules = json.load(f)
    
    new_rule = request.dict()
    if not new_rule["rule_id"]:
        new_rule["rule_id"] = str(uuid.uuid4().hex[:8])
    
    rules.append(new_rule)
    
    with open(rules_file, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    
    return {"message": "规则添加成功", "rule": new_rule}

@app.put("/api/rules/{rule_id}")
async def update_rule(rule_id: str, request: ConversationRule):
    rules_file = os.path.join(os.path.dirname(__file__), "../data/rules.json")
    
    if not os.path.exists(rules_file):
        raise HTTPException(status_code=404, detail="规则文件不存在")
    
    with open(rules_file, "r", encoding="utf-8") as f:
        rules = json.load(f)
    
    for i, rule in enumerate(rules):
        if rule["rule_id"] == rule_id:
            rules[i] = request.dict()
            rules[i]["rule_id"] = rule_id
            
            with open(rules_file, "w", encoding="utf-8") as f:
                json.dump(rules, f, ensure_ascii=False, indent=2)
            
            return {"message": "规则更新成功", "rule": rules[i]}
    
    raise HTTPException(status_code=404, detail="规则不存在")

@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: str):
    rules_file = os.path.join(os.path.dirname(__file__), "../data/rules.json")
    
    if not os.path.exists(rules_file):
        raise HTTPException(status_code=404, detail="规则文件不存在")
    
    with open(rules_file, "r", encoding="utf-8") as f:
        rules = json.load(f)
    
    original_count = len(rules)
    rules = [r for r in rules if r["rule_id"] != rule_id]
    
    if len(rules) == original_count:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    with open(rules_file, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    
    return {"message": "规则删除成功"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "conversation-robot-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
