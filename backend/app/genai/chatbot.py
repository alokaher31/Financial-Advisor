"""
Financial advisor chatbot implementation using Groq LLM.
Handles conversational queries with customer context and what-if scenario detection.
"""

import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.genai.llm_client import get_llm_client
from app.genai.retriever import get_customer_context
from app.genai.prompts.chatbot_system_prompt import get_chatbot_system_prompt
from app.genai.whatif_analyzer import analyze_and_narrate_whatif
from app.data.data_loader import load_historical_data


def detect_whatif_intent(user_message: str) -> Optional[Dict[str, Any]]:
    """
    Detect if the user is asking a what-if question and extract parameters.
    
    Looks for patterns like:
    - "what if I increase/decrease X to Y"
    - "what if I invest Z more"
    - "what happens if I change X to Y"
    
    Args:
        user_message: The user's question
        
    Returns:
        Dictionary with what-if parameters if detected, otherwise None:
        {
            "parameter": str,  # What parameter to adjust
            "value": float,    # New value (if specific number found)
            "direction": str   # "increase" or "decrease"
        }
    """
    message_lower = user_message.lower()
    
    # What-if trigger phrases
    whatif_triggers = [
        "what if",
        "what happens if",
        "suppose i",
        "if i increase",
        "if i decrease",
        "if i invest",
        "if i save",
        "if i spend",
    ]
    
    # Check if message contains what-if trigger
    has_trigger = any(trigger in message_lower for trigger in whatif_triggers)
    if not has_trigger:
        return None
    
    # Parameter patterns to detect
    parameter_patterns = {
        "monthly_investment": [
            r"invest(?:ment)?",
            r"sav(?:e|ing|ings)",
            r"monthly.*(?:invest|sav)",
        ],
        "monthly_expenses": [
            r"expens(?:e|es)",
            r"spend(?:ing)?",
            r"monthly.*(?:expens|spend)",
        ],
        "monthly_income": [
            r"income",
            r"salary",
            r"earn(?:ing|ings)?",
        ],
        "time_horizon_years": [
            r"(?:time.*)?horizon",
            r"years?",
            r"timeline",
            r"duration",
        ],
        "target_amount": [
            r"target",
            r"goal.*amount",
            r"corpus",
        ],
    }
    
    detected_parameter = None
    for param, patterns in parameter_patterns.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                detected_parameter = param
                break
        if detected_parameter:
            break
    
    # Detect direction (increase/decrease)
    direction = None
    if any(word in message_lower for word in ["increase", "more", "add", "higher", "raise"]):
        direction = "increase"
    elif any(word in message_lower for word in ["decrease", "less", "reduce", "lower", "cut"]):
        direction = "decrease"
    
    # Try to extract numeric value
    # Look for patterns like "₹50000", "50000", "50k", "50 thousand"
    value = None
    
    # Match currency patterns: ₹50000 or 50000
    currency_match = re.search(r'₹?\s*(\d{1,3}(?:,\d{3})*|\d+)(?:\s*(?:k|thousand|lakh|crore))?', user_message)
    if currency_match:
        value_str = currency_match.group(1).replace(',', '')
        value = float(value_str)
        
        # Handle k, thousand, lakh, crore multipliers
        if 'k' in message_lower or 'thousand' in message_lower:
            value *= 1000
        elif 'lakh' in message_lower:
            value *= 100000
        elif 'crore' in message_lower:
            value *= 10000000
    
    # Only return if we detected a parameter
    if detected_parameter:
        return {
            "parameter": detected_parameter,
            "value": value,
            "direction": direction,
        }
    
    return None


def get_chatbot_response(
    customer_id: int,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    db: Session,
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    """
    Generate a chatbot response using Groq LLM with customer context.
    
    Handles two types of queries:
    1. General financial questions - uses customer context and LLM
    2. What-if questions - detects intent, runs what-if analysis, narrates result
    
    Args:
        customer_id: ID of the customer
        user_message: The user's question
        conversation_history: List of previous messages (dict with 'role' and 'content')
        db: Database session
        temperature: LLM temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        The chatbot's response text
        
    Raises:
        ValueError: If customer not found
        Exception: If LLM call fails
    """
    # Detect what-if intent first
    whatif_intent = detect_whatif_intent(user_message)
    
    # Fetch customer context
    try:
        context = get_customer_context(customer_id, db)
    except ValueError as e:
        return f"I couldn't find your profile. {str(e)}"
    
    # Handle what-if scenarios
    if whatif_intent and context.get("goals") and context.get("plans", {}).get("active_plan"):
        return _handle_whatif_query(
            whatif_intent=whatif_intent,
            context=context,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    # Handle general queries
    return _handle_general_query(
        user_message=user_message,
        context=context,
        conversation_history=conversation_history,
        temperature=temperature,
        max_tokens=max_tokens
    )


def _handle_whatif_query(
    whatif_intent: Dict[str, Any],
    context: Dict[str, Any],
    user_message: str,
    temperature: float,
    max_tokens: int
) -> str:
    """
    Handle what-if scenario queries by running analysis and narrating results.
    
    Args:
        whatif_intent: Detected what-if parameters
        context: Customer context
        user_message: Original user message
        temperature: LLM temperature
        max_tokens: Maximum tokens
        
    Returns:
        Narrated what-if analysis result
    """
    profile = context["profile"]
    goals = context["goals"]
    active_plan = context["plans"]["active_plan"]
    risk_category = context.get("risk_assessment", {}).get("risk_category", "Moderate")
    
    # If no specific value was detected, ask for clarification
    if whatif_intent["value"] is None:
        return (
            f"I understand you'd like to explore a what-if scenario regarding {whatif_intent['parameter'].replace('_', ' ')}. "
            f"To help you better, could you please specify the exact amount you'd like to test? "
            f"For example: 'What if I invest ₹50,000 per month?'"
        )
    
    # Use the first goal for simplicity (in production, might need to select specific goal)
    goal = goals[0] if goals else None
    if not goal:
        return "I need a financial goal to run a what-if analysis. Please set a goal first."
    
    # Prepare data for what-if analyzer
    customer_profile_dict = {
        "monthly_income": profile["monthly_income"],
        "monthly_expenses": profile["monthly_expenses"],
    }
    
    goal_dict = {
        "target_amount": goal["target_amount"],
        "current_amount": goal["current_savings"],
        "time_horizon_years": goal["time_horizon_years"],
    }
    
    historical_data = load_historical_data()
    
    # Map detected parameter to what the analyzer expects
    parameter_mapping = {
        "monthly_investment": "current_monthly_investment",
        "monthly_expenses": "monthly_expenses",
        "monthly_income": "monthly_income",
        "time_horizon_years": "time_horizon_years",
        "target_amount": "target_amount",
    }
    
    adjustment_parameter = parameter_mapping.get(
        whatif_intent["parameter"],
        whatif_intent["parameter"]
    )
    
    try:
        # Run what-if analysis with narration
        result = analyze_and_narrate_whatif(
            customer_profile=customer_profile_dict,
            goal=goal_dict,
            risk_category=risk_category,
            historical_data=historical_data,
            adjustment_parameter=adjustment_parameter,
            adjusted_value=whatif_intent["value"],
            plan_name=active_plan["plan_name"],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return result["narration"]
        
    except Exception as e:
        # Fallback to general query if what-if analysis fails
        return (
            f"I understand you're asking about a what-if scenario, but I encountered an issue: {str(e)}. "
            f"Let me try to answer your question generally instead.\n\n"
            + _handle_general_query(
                user_message=user_message,
                context=context,
                conversation_history=[],
                temperature=temperature,
                max_tokens=max_tokens
            )
        )


def _handle_general_query(
    user_message: str,
    context: Dict[str, Any],
    conversation_history: List[Dict[str, str]],
    temperature: float,
    max_tokens: int
) -> str:
    """
    Handle general financial queries using LLM with customer context.
    
    Args:
        user_message: The user's question
        context: Customer context
        conversation_history: Previous conversation
        temperature: LLM temperature
        max_tokens: Maximum tokens
        
    Returns:
        LLM-generated response
    """
    # Format customer context for system prompt
    customer_context = _format_customer_context(context)
    
    # Get system prompt with customer context
    system_prompt = get_chatbot_system_prompt(customer_context)
    
    # Build conversation with history
    llm_client = get_llm_client()
    
    # Format conversation history for context
    history_context = ""
    if conversation_history:
        history_context = "\n\n## Recent Conversation:\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "Customer" if msg["role"] == "user" else "Assistant"
            history_context += f"{role}: {msg['content']}\n"
    
    # Build the full prompt
    full_prompt = f"{history_context}\n\nCustomer: {user_message}"
    
    try:
        response = llm_client.generate_response(
            prompt=full_prompt,
            system_message=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response
        
    except Exception as e:
        return (
            f"I apologize, but I'm having trouble processing your question right now. "
            f"Error: {str(e)}. Please try again or rephrase your question."
        )


def _format_customer_context(context: Dict[str, Any]) -> str:
    """
    Format customer context into a readable string for the LLM.
    
    Args:
        context: Customer context dictionary
        
    Returns:
        Formatted context string
    """
    profile = context["profile"]
    risk = context.get("risk_assessment")
    goals = context.get("goals", [])
    active_plan = context.get("plans", {}).get("active_plan")
    
    formatted = f"""
**Profile:**
- Name: {profile['name']}
- Age: {profile['age']} years
- Occupation: {profile['occupation']}
- Monthly Income: ₹{profile['monthly_income']:,.2f}
- Monthly Expenses: ₹{profile['monthly_expenses']:,.2f}
- Net Worth: ₹{profile['net_worth']:,.2f}
- Monthly Surplus: ₹{profile['monthly_surplus']:,.2f}
- Savings Rate: {profile['savings_rate']:.1f}%
"""
    
    if risk:
        formatted += f"""
**Risk Profile:**
- Risk Category: {risk['risk_category']}
- Risk Score: {risk['risk_score']}
"""
    
    if goals:
        formatted += "\n**Financial Goals:**\n"
        for i, goal in enumerate(goals, 1):
            formatted += f"""
{i}. {goal['goal_name']} ({goal['goal_type']})
   - Target: ₹{goal['target_amount']:,.2f}
   - Current Savings: ₹{goal['current_savings']:,.2f}
   - Time Horizon: {goal['time_horizon_years']} years
   - Priority: {goal['priority']}
   - Required Monthly Savings: ₹{goal['required_monthly_savings']:,.2f}
   - Achievable: {'Yes' if goal['is_achievable'] else 'No'}
"""
    
    if active_plan:
        formatted += f"""
**Active Investment Plan:**
- Plan: {active_plan['plan_name']} ({active_plan['risk_level']} Risk)
- Expected Return: {active_plan['blended_expected_return']}%
- Current Monthly Investment: ₹{active_plan['current_monthly_investment']:,.2f}
- Projected Corpus: ₹{active_plan['projected_corpus']:,.2f}
- Gap vs Target: ₹{active_plan['gap_vs_target']:,.2f}
"""
    
    return formatted.strip()
