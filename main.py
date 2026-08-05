from mcp_server import LidyaMCPTools
from rag import process_and_query_document
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import get_db, SentimentRecord, User
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
import joblib
import os

app = FastAPI(
    title="Lidya AI - Secure Microservice Platform",
    description="FastAPI, JWT Authentication, SQLAlchemy ve ML tabanlı Duygu Analizi API Servisi",
    version="2.0.0"
)

# Pydantic Modelleri (Input Validation & Sanitization)
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=2, description="Analiz edilecek metin")

# Model Yükleme
MODEL_PATH = "sentiment_model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

model = joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
vectorizer = joblib.load(VECTORIZER_PATH) if os.path.exists(VECTORIZER_PATH) else None

@app.get("/")
def root():
    return {"status": "online", "service": "Lidya Secure API v2.0"}

# --- AUTH ENDPOINTS ---

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten alınmış.")
    
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "Kullanıcı başarıyla oluşturuldu."}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı kullanıcı adı veya şifre.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PROTECTED ML ENDPOINTS ---

@app.post("/predict")
def predict_sentiment(
    req: SentimentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="ML modeli yüklenemedi.")
    
    X_vec = vectorizer.transform([req.text])
    prediction = model.predict(X_vec)[0]
    
    record = SentimentRecord(text=req.text, sentiment=str(prediction))
    db.add(record)
    db.commit()
    
    return {
        "user": current_user.username,
        "text": req.text,
        "sentiment": str(prediction)
    }

@app.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(SentimentRecord).order_by(SentimentRecord.id.desc()).limit(20).all()
    return [{"id": r.id, "text": r.text, "sentiment": r.sentiment, "created_at": r.created_at} for r in records]

# --- RAG ENDPOINT ---
class RAGRequest(BaseModel):
    document: str = Field(..., description="Kaynak doküman metni")
    question: str = Field(..., description="Dokümana sorulacak soru")

@app.post("/rag-query")
def rag_query(
    req: RAGRequest,
    current_user: User = Depends(get_current_user)
):
    answer = process_and_query_document(req.document, req.question)
    return {
        "user": current_user.username,
        "question": req.question,
        "answer": answer
    }

# --- MCP (MODEL CONTEXT PROTOCOL) ENDPOINTS ---

@app.get("/mcp/tools")
def mcp_list_tools(current_user: User = Depends(get_current_user)):
    """LLM veya MCP İstemcileri için kullanılabilir araçların listesini döner."""
    return {
        "tools": [
            {
                "name": "list_recent_sentiments",
                "description": "Veritabanındaki son duygu analizi kayıtlarını listeler.",
                "parameters": {"limit": "integer (varsayılan: 5)"}
            },
            {
                "name": "get_system_stats",
                "description": "Sistemdeki toplam analiz ve kayıt istatistiklerini getirir.",
                "parameters": {}
            }
        ]
    }

class MCPCallRequest(BaseModel):
    tool_name: str
    arguments: dict = {}

@app.post("/mcp/call")
def mcp_call_tool(
    req: MCPCallRequest,
    current_user: User = Depends(get_current_user)
):
    """MCP standardına göre istenen aracı çalıştırır ve sonucunu döner."""
    if req.tool_name == "list_recent_sentiments":
        limit = req.arguments.get("limit", 5)
        result = LidyaMCPTools.list_recent_sentiments(limit=limit)
        return {"tool": req.tool_name, "result": result}
    
    elif req.tool_name == "get_system_stats":
        result = LidyaMCPTools.get_system_stats()
        return {"tool": req.tool_name, "result": result}
    
    else:
        raise HTTPException(status_code=404, detail=f"'{req.tool_name}' adında bir MCP aracı bulunamadı.")
