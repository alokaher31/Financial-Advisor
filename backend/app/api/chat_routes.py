"""
API routes for chat/conversational AI.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db import crud
from app.models import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ChatMessageCreate,
    MessageRole,
    ChatHistoryRequest,
    ChatSession,
)
from app.utils.logger import logger

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with the financial advisor AI.
    
    Handles customer questions and provides personalized financial guidance.
    Maintains conversation history per session.
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, request.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {request.customer_id} not found"
            )
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Save user message
        user_message = ChatMessageCreate(
            customer_id=request.customer_id,
            role=MessageRole.USER,
            content=request.message,
            session_id=session_id,
        )
        crud.create_chat_message(db, user_message)
        
        # Get conversation history if requested
        context_messages = []
        if request.include_context and request.max_history_messages > 0:
            recent_messages = crud.get_recent_chat_messages(
                db, 
                request.customer_id, 
                session_id, 
                limit=request.max_history_messages
            )
            context_messages = list(reversed(recent_messages))
        
        # Call real chatbot with Groq LLM
        from app.genai.chatbot import get_chatbot_response
        
        # Format conversation history for chatbot
        formatted_history = []
        for msg in context_messages:
            formatted_history.append({
                "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
                "content": msg.message if hasattr(msg, 'message') else msg.content
            })
        
        # Generate AI response
        try:
            assistant_response = get_chatbot_response(
                customer_id=request.customer_id,
                user_message=request.message,
                conversation_history=formatted_history,
                db=db
            )
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            # Fallback response if chatbot fails
            assistant_response = (
                f"I apologize, but I'm experiencing technical difficulties. "
                f"Please try again in a moment. If the issue persists, please contact support."
            )
        
        # Save assistant message
        assistant_message = ChatMessageCreate(
            customer_id=request.customer_id,
            role=MessageRole.ASSISTANT,
            content=assistant_response,
            session_id=session_id,
        )
        crud.create_chat_message(db, assistant_message)
        
        logger.info(f"Chat interaction completed for customer {request.customer_id}, session {session_id}")
        
        return ChatResponse(
            message=assistant_response,
            session_id=session_id,
            customer_id=request.customer_id,
            timestamp=datetime.utcnow(),
            context_used=request.include_context,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.post("/history", response_model=List[ChatMessage])
def get_chat_history(
    request: ChatHistoryRequest,
    db: Session = Depends(get_db)
):
    """
    Get chat history for a customer.
    
    Can filter by session_id or get all conversations.
    """
    # Verify customer exists
    customer = crud.get_customer_profile(db, request.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {request.customer_id} not found"
        )
    
    messages = crud.get_chat_history(
        db,
        customer_id=request.customer_id,
        session_id=request.session_id,
        skip=request.offset,
        limit=request.limit,
    )
    
    return messages


@router.get("/sessions/{customer_id}", response_model=List[str])
def get_customer_sessions(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get all chat session IDs for a customer."""
    # Verify customer exists
    customer = crud.get_customer_profile(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    sessions = crud.get_customer_sessions(db, customer_id)
    return sessions


@router.delete("/sessions/{customer_id}/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_session(
    customer_id: int,
    session_id: str,
    db: Session = Depends(get_db)
):
    """Delete all messages in a chat session."""
    success = crud.delete_chat_session(db, customer_id, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chat session found for customer {customer_id} with session {session_id}"
        )
    logger.info(f"Chat session deleted: customer={customer_id}, session={session_id}")
    return None
