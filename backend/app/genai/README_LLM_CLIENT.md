# LLM Client Usage Guide

## Overview

The `llm_client.py` module provides a reusable interface for making LLM calls using the Groq API with the `openai/gpt-oss-120b` model.

## Configuration

The API key is loaded from the `GROQ_API_KEY` environment variable in the `.env` file. **Never hardcode or expose the API key.**

## Usage

### Quick Start (Recommended)

```python
from app.genai.llm_client import generate_llm_response

# Simple response generation
response = generate_llm_response("What is a savings account?")
print(response)

# With system message
response = generate_llm_response(
    prompt="Explain compound interest",
    system_message="You are a financial advisor. Be concise and clear.",
    temperature=0.7,
    max_tokens=500
)
print(response)
```

### Using the Client Class

```python
from app.genai.llm_client import LLMClient

# Initialize client
client = LLMClient()

# Generate response with retry logic
response = client.generate_response(
    prompt="What are the benefits of diversification?",
    system_message="You are a helpful financial assistant.",
    temperature=0.7,
    max_tokens=1000
)

# Generate response with fallback
response = client.generate_response_with_fallback(
    prompt="Explain risk tolerance",
    fallback_response="Unable to generate response. Please try again.",
    temperature=0.5
)
```

### Using the Singleton Pattern

```python
from app.genai.llm_client import get_llm_client

# Get shared client instance
client = get_llm_client()

# Use the client
response = client.generate_response("Tell me about bonds")
```

## Features

- **Automatic Retry Logic**: Retries failed requests up to 3 times with exponential backoff
- **Error Handling**: Gracefully handles rate limits, connection errors, and API errors
- **Fallback Responses**: Optional fallback messages when LLM calls fail
- **Singleton Pattern**: Reusable client instance across the application
- **Environment-based Configuration**: API key loaded from environment variables

## Parameters

- `prompt` (str): The user question or prompt
- `system_message` (str, optional): System message to set context
- `temperature` (float, default=0.7): Sampling temperature (0.0-2.0)
- `max_tokens` (int, default=4096): Maximum tokens in response
- `**kwargs`: Additional arguments to pass to the Groq API

## Model Information

- **Provider**: Groq
- **Model**: `openai/gpt-oss-120b`
- **Note**: This model uses reasoning tokens, so ensure adequate max_tokens (recommended: 100+)

## Testing

Run the test suite:

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run all tests
$env:PYTHONPATH="$PWD"
python -m pytest tests/test_llm_client.py -v

# Run specific test
python -m pytest tests/test_llm_client.py::test_groq_connection -v -s
```

## Security Notes

- API key is loaded from environment variables only
- Never commit the `.env` file to version control
- The API key is not logged or exposed in error messages
