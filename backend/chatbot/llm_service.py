import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # type: ignore
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # type: ignore

from rag_service import get_rag_service

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("LLMService")
logging.basicConfig(level=logging.INFO)

# System prompt defining AI's persona, rules, constraints, and RAG grounding
SYSTEM_PROMPT = """You are CogAdvisor, an intelligent, empathetic, and knowledgeable Financial Planning Assistant.

Your responsibilities:
1. Provide personalized financial insights, budgeting advice, savings strategies, debt management, and investment education.
2. Adapt your tone to be professional, encouraging, clear, and easy to understand.
3. Tailor your recommendations based on the user's financial profile, goals, and risk tolerance if provided.
4. Ground your advice using the verified Financial Knowledge Base context provided below whenever applicable.

Important Constraints & Guidelines:
- Do NOT provide formal certified tax, legal, or guaranteed investment return advice.
- Always include a brief reminder or disclaimer when discussing specific investment instruments (e.g. 'Past performance does not guarantee future results').
- Be concise, well-structured, and use bullet points or numbered lists where helpful.

---
Verified Financial Knowledge Base (RAG Context):
{retrieved_context}
---

User Context:
- User Profile: {user_profile}
- Financial Goals: {goals}
- Risk Tolerance: {risk_tolerance}
"""

# Candidate models in order of preference
DEFAULT_MODELS = ["gemini-3.5-flash", "gemini-3-flash-preview", "gemini-3.1-flash-lite", "gemma-4-26b-a4b-it"]

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is not set. Please set it in your .env file.")
        
        # Build prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

    def _get_chain(self, model_name: str):
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            google_api_key=self.api_key
        )
        return self.prompt | llm

    def generate_reply(
        self,
        question: str,
        user_profile: Dict[str, Any] = None,
        goals: List[Dict[str, Any]] = None,
        risk_tolerance: str = "moderate",
        chat_history: List[Dict[str, str]] = None,
        enable_rag: bool = True
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generates an AI response given the user question, context, conversation history, and RAG knowledge.
        Returns a tuple of (reply_text, sources_list).
        """
        # Format chat history into LangChain message objects
        formatted_history = []
        if chat_history:
            for msg in chat_history:
                role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "user")
                content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
                if role == "user":
                    formatted_history.append(HumanMessage(content=content))
                elif role in ["assistant", "bot", "ai"]:
                    formatted_history.append(AIMessage(content=content))
                elif role == "system":
                    formatted_history.append(SystemMessage(content=content))

        # Retrieve RAG context from ChromaDB
        sources: List[Dict[str, Any]] = []
        retrieved_context_str = "No internal knowledge base documents retrieved for this query."
        if enable_rag:
            try:
                rag = get_rag_service()
                sources = rag.retrieve_context(question, top_k=3)
                retrieved_context_str = rag.format_retrieved_context(question, top_k=3)
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        # Format context objects as readable text
        profile_str = str(user_profile) if user_profile else "Not specified"
        goals_str = str(goals) if goals else "Not specified"
        risk_str = risk_tolerance if risk_tolerance else "Moderate"

        input_payload = {
            "question": question,
            "retrieved_context": retrieved_context_str,
            "user_profile": profile_str,
            "goals": goals_str,
            "risk_tolerance": risk_str,
            "chat_history": formatted_history
        }

        # Model preference hierarchy
        preferred = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        model_list = [preferred] + [m for m in DEFAULT_MODELS if m != preferred]

        last_error = None
        for model in model_list:
            try:
                chain = self._get_chain(model)
                response = chain.invoke(input_payload)
                raw_content = response.content
                if isinstance(raw_content, str):
                    return raw_content, sources
                elif isinstance(raw_content, list):
                    text_parts = []
                    for part in raw_content:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(part["text"])
                        elif isinstance(part, str):
                            text_parts.append(part)
                    reply_text = "".join(text_parts) if text_parts else str(raw_content)
                    return reply_text, sources
                return str(raw_content), sources
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All model attempts failed. Last error: {last_error}")

# Singleton LLM service instance
llm_service = None

def get_llm_service() -> LLMService:
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service

