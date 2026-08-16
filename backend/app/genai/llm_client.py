"""
LLM Client for Groq API integration.
Provides a reusable interface for making LLM calls with error handling and retry logic.
"""

import os
import time
from typing import Optional, Dict, Any
from groq import Groq, APIError, RateLimitError, APIConnectionError


class LLMClient:
    """
    Client for interacting with Groq API using openai/gpt-oss-120b model.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-oss-120b"):
        """
        Initialize the LLM client.
        
        Args:
            api_key: Groq API key. If None, loads from GROQ_API_KEY environment variable.
            model: Model to use for completions. Default: openai/gpt-oss-120b
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it in environment or pass to constructor.")
        
        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM with retry logic.
        
        Args:
            prompt: The user prompt/question
            system_message: Optional system message to set context
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional arguments to pass to the API
        
        Returns:
            str: The generated response text
            
        Raises:
            Exception: If all retry attempts fail
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                message = response.choices[0].message
                
                # The openai/gpt-oss-120b model uses reasoning tokens
                # Content may be empty if only reasoning is provided
                # Check both content and reasoning fields
                content = message.content
                
                # If content is empty or None, try to get reasoning
                if not content and hasattr(message, 'reasoning') and message.reasoning:
                    content = message.reasoning
                
                if content is None:
                    return ""
                    
                return content.strip()
                
            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                    
            except APIConnectionError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                    
            except APIError as e:
                last_error = e
                # For general API errors, retry with backoff
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
            except Exception as e:
                # For unexpected errors, fail immediately
                raise Exception(f"Unexpected error in LLM call: {str(e)}") from e
        
        # If all retries failed, raise the last error
        raise Exception(f"Failed after {self.max_retries} attempts: {str(last_error)}") from last_error
    
    def generate_response_with_fallback(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        fallback_response: str = "I apologize, but I'm unable to process your request at the moment. Please try again later.",
        **kwargs
    ) -> str:
        """
        Generate a response with a fallback message if all attempts fail.
        
        Args:
            prompt: The user prompt/question
            system_message: Optional system message
            fallback_response: Message to return if LLM call fails
            **kwargs: Additional arguments to pass to generate_response
        
        Returns:
            str: The generated response or fallback message
        """
        try:
            return self.generate_response(prompt, system_message, **kwargs)
        except Exception as e:
            # Log the error (in production, use proper logging)
            print(f"LLM call failed: {str(e)}")
            return fallback_response


# Singleton instance for reuse across the application
_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """
    Get or create a singleton LLM client instance.
    
    Returns:
        LLMClient: The shared LLM client instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = LLMClient()
    return _client_instance


def generate_llm_response(prompt: str, system_message: Optional[str] = None, **kwargs) -> str:
    """
    Convenience function to generate an LLM response using the singleton client.
    
    Args:
        prompt: The user prompt/question
        system_message: Optional system message
        **kwargs: Additional arguments to pass to the client
    
    Returns:
        str: The generated response text
    """
    client = get_llm_client()
    return client.generate_response(prompt, system_message, **kwargs)
