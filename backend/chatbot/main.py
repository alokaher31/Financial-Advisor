from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import UserInputPayload, CollectorResponse
from data_collector import collector_service
from rag_service import get_rag_service

app = FastAPI(
    title="CogAdvisor - RAG Financial Planning API",
    description="Intelligent financial advisory backend powered by LangChain, Google Gemini, and ChromaDB RAG vector search.",
    version="2.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "CogAdvisor RAG Chatbot API",
        "docs_url": "/docs",
        "health_check": "/health",
        "chat_endpoint": "/api/chat",
        "rag_stats_endpoint": "/api/rag/stats",
        "ingest_endpoint": "/api/ingest"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "CogAdvisor Financial Planning API"}

@app.get("/api/rag/stats")
def rag_stats():
    """
    Returns statistics about the ChromaDB vector store collection and indexed documents.
    """
    try:
        rag = get_rag_service()
        return rag.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
def trigger_ingestion():
    """
    Triggers re-indexing of all knowledge base markdown/text documents into ChromaDB.
    """
    try:
        rag = get_rag_service()
        result = rag.ingest_directory()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=CollectorResponse)
def chat_endpoint(payload: UserInputPayload):
    """
    Main chat endpoint: ingests user query + context + RAG knowledge, runs through LangChain Gemini, and returns AI reply with citations.
    """
    try:
        response = collector_service.collect_and_respond(payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/collect-input", response_model=CollectorResponse)
def collect_input_endpoint(payload: UserInputPayload):
    """
    Alias endpoint for data collection and response generation.
    """
    return chat_endpoint(payload)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
