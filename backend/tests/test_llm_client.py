"""
Tests for the LLM client module.
"""

import os
import pytest
from dotenv import load_dotenv
from app.genai.llm_client import LLMClient, get_llm_client, generate_llm_response

# Load environment variables from .env file
load_dotenv()


def test_llm_client_initialization():
    """Test that LLM client initializes correctly with environment variable."""
    # Ensure GROQ_API_KEY is set
    api_key = os.getenv("GROQ_API_KEY")
    assert api_key is not None, "GROQ_API_KEY must be set in environment"
    
    client = LLMClient()
    assert client.api_key == api_key
    assert client.model == "openai/gpt-oss-120b"
    assert client.client is not None


def test_llm_client_custom_model():
    """Test that custom model can be specified."""
    client = LLMClient(model="custom-model")
    assert client.model == "custom-model"


def test_llm_client_missing_api_key():
    """Test that client raises error when API key is missing."""
    # Temporarily remove API key from environment
    original_key = os.environ.get("GROQ_API_KEY")
    if original_key:
        del os.environ["GROQ_API_KEY"]
    
    try:
        with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
            LLMClient()
    finally:
        # Restore API key
        if original_key:
            os.environ["GROQ_API_KEY"] = original_key


def test_generate_response_basic():
    """Test basic response generation from Groq API."""
    client = LLMClient()
    
    prompt = "What is 2+2? Answer with just the number."
    response = client.generate_response(prompt, temperature=0.1, max_tokens=10)
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\nPrompt: {prompt}")
    print(f"Response: {response}")


def test_generate_response_with_system_message():
    """Test response generation with system message."""
    client = LLMClient()
    
    system_message = "You are a helpful financial assistant. Keep answers concise."
    prompt = "What is a savings account?"
    
    response = client.generate_response(
        prompt,
        system_message=system_message,
        temperature=0.5,
        max_tokens=100
    )
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\nSystem: {system_message}")
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")


def test_generate_response_with_fallback():
    """Test fallback response on error."""
    client = LLMClient()
    
    # Test successful call
    response = client.generate_response_with_fallback(
        "Say 'hello'",
        temperature=0.1,
        max_tokens=50
    )
    assert "hello" in response.lower()
    
    # Test with invalid model to trigger fallback
    client.model = "invalid-model-xyz"
    response = client.generate_response_with_fallback(
        "This should fail",
        fallback_response="Fallback activated"
    )
    assert response == "Fallback activated"


def test_singleton_client():
    """Test that get_llm_client returns the same instance."""
    client1 = get_llm_client()
    client2 = get_llm_client()
    
    assert client1 is client2
    assert client1.model == "openai/gpt-oss-120b"


def test_convenience_function():
    """Test the convenience function for generating responses."""
    response = generate_llm_response(
        "Name one primary color. Answer with just one word.",
        temperature=0.1,
        max_tokens=10
    )
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    print(f"\nConvenience function response: {response}")


def test_groq_connection():
    """
    Integration test to verify connection to Groq API.
    This confirms the API key is valid and the service is accessible.
    """
    client = LLMClient()
    
    test_prompt = "Say hello"
    
    try:
        response = client.generate_response(
            test_prompt,
            temperature=0.5,
            max_tokens=100
        )
        
        assert response is not None
        assert len(response) > 0
        print(f"\n✓ Groq API connection successful!")
        print(f"  Model: {client.model}")
        print(f"  Response: {response}")
        
    except Exception as e:
        pytest.fail(f"Failed to connect to Groq API: {str(e)}")


if __name__ == "__main__":
    # Run the connection test directly
    print("Testing Groq API connection...")
    test_groq_connection()
