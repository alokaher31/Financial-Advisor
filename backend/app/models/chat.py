"""
Chat/Conversational AI Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageBase(BaseModel):
    """Base model for chat message data."""
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., min_length=1, max_length=10000, description="Message content")


class ChatMessageCreate(ChatMessageBase):
    """Model for creating a new chat message."""
    customer_id: int = Field(..., gt=0, description="ID of the customer")
    session_id: Optional[str] = Field(None, description="Chat session identifier")


class ChatMessage(ChatMessageBase):
    """Model for chat message response with database fields."""
    id: int
    customer_id: int
    session_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Request model for chat interaction."""
    customer_id: int = Field(..., gt=0, description="ID of the customer")
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session identifier for context")
    include_context: bool = Field(True, description="Whether to include customer profile context")
    max_history_messages: int = Field(10, ge=0, le=50, description="Number of previous messages to include")


class ChatResponse(BaseModel):
    """Response model for chat interaction."""
    message: str = Field(..., description="Assistant's response")
    session_id: str = Field(..., description="Chat session identifier")
    customer_id: int
    timestamp: datetime
    context_used: bool = Field(..., description="Whether customer context was used")


class ChatSession(BaseModel):
    """Model representing a chat session."""
    session_id: str = Field(..., description="Unique session identifier")
    customer_id: int
    messages: List[ChatMessage] = Field(..., description="List of messages in this session")
    created_at: datetime
    last_activity: datetime
    message_count: int = Field(..., ge=0)


class ChatHistoryRequest(BaseModel):
    """Request model for retrieving chat history."""
    customer_id: int = Field(..., gt=0)
    session_id: Optional[str] = Field(None, description="Specific session ID, or None for all sessions")
    limit: int = Field(50, ge=1, le=500, description="Maximum number of messages to retrieve")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class ConversationSummary(BaseModel):
    """AI-generated summary of a conversation."""
    session_id: str
    customer_id: int
    message_count: int
    time_span: str = Field(..., description="Time span of the conversation")
    summary: str = Field(..., description="AI-generated summary of the conversation")
    key_topics: List[str] = Field(..., description="Key topics discussed")
    action_items: List[str] = Field(..., description="Action items identified")
    sentiment: str = Field(..., description="Overall sentiment of the conversation")
