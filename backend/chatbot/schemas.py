from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender (e.g., 'user', 'assistant', 'system')")
    content: str = Field(..., description="Text content of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class UserInputPayload(BaseModel):
    """
    Schema for collecting incoming user input and associated frontend context.
    """
    message: str = Field(..., min_length=1, description="User's query or prompt from frontend")
    session_id: Optional[str] = Field(default="default_session", description="Unique session ID for tracking conversation")
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="Optional user financial profile context")
    goals: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional financial goals list")
    risk_tolerance: Optional[str] = Field(default=None, description="Optional risk tolerance level")
    chat_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation turns")
    enable_rag: Optional[bool] = Field(default=True, description="Whether to augment query with ChromaDB knowledge base")

class CollectorResponse(BaseModel):
    """
    Schema returned after successfully collecting and processing frontend user input.
    """
    status: str = "success"
    session_id: str
    message_received: str
    collected_context: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reply: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = Field(default=[], description="Retrieved RAG knowledge chunks and sources")
