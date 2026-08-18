import logging
from typing import Dict, Any, List
from schemas import UserInputPayload, CollectorResponse
from llm_service import get_llm_service

logger = logging.getLogger("ChatbotDataCollector")
logging.basicConfig(level=logging.INFO)

class DataCollector:
    """
    Service to receive, validate, log, and process frontend user inputs with LangChain Gemini LLM.
    """
    def __init__(self):
        # In-memory store for active session states
        self.session_data: Dict[str, Dict[str, Any]] = {}

    def collect_and_respond(self, payload: UserInputPayload) -> CollectorResponse:
        """
        Collects user input alongside frontend context (profile, goals, risk tolerance),
        invokes the LangChain Gemini LLM, and returns the generated answer.
        """
        session_id = payload.session_id or "default_session"
        
        # Structure collected context
        user_profile = payload.user_profile or {}
        goals = payload.goals or []
        risk_tolerance = payload.risk_tolerance or "moderate"

        # Initialize session state if first message
        if session_id not in self.session_data:
            self.session_data[session_id] = {
                "history": [],
                "profile": user_profile,
                "goals": goals,
                "risk_tolerance": risk_tolerance
            }
        
        # Combine provided history with session history
        history = self.session_data[session_id]["history"]
        if payload.chat_history:
            history = [{"role": msg.role, "content": msg.content} for msg in payload.chat_history]

        logger.info(f"Received query from session [{session_id}]: {payload.message}")

        # Invoke LLM with RAG
        sources = []
        try:
            llm = get_llm_service()
            reply_text, sources = llm.generate_reply(
                question=payload.message,
                user_profile=user_profile or self.session_data[session_id]["profile"],
                goals=goals or self.session_data[session_id]["goals"],
                risk_tolerance=risk_tolerance or self.session_data[session_id]["risk_tolerance"],
                chat_history=history,
                enable_rag=payload.enable_rag if payload.enable_rag is not None else True
            )
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            reply_text = f"Error generating response: {str(e)}"

        # Append interaction to history
        self.session_data[session_id]["history"].append({"role": "user", "content": payload.message})
        self.session_data[session_id]["history"].append({"role": "assistant", "content": reply_text})

        collected_context = {
            "user_profile": user_profile,
            "goals": goals,
            "risk_tolerance": risk_tolerance,
            "history_length": len(self.session_data[session_id]["history"]),
            "rag_enabled": payload.enable_rag if payload.enable_rag is not None else True
        }

        return CollectorResponse(
            status="success",
            session_id=session_id,
            message_received=payload.message,
            collected_context=collected_context,
            reply=reply_text,
            sources=sources
        )

# Global singleton instance
collector_service = DataCollector()
