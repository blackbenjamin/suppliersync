
import time, os, json
from openai import OpenAI
from openai import APITimeoutError, APIConnectionError, APIError
from typing import Optional

# Model selection from env (defaults to gpt-4o-mini)
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Lazy client initialization
_client = None

def _get_client():
    """
    Get or create OpenAI client (lazy initialization).
    
    Uses singleton pattern to avoid creating multiple clients.
    Client is only created when first needed, allowing the service
    to start even if OPENAI_API_KEY is not immediately available.
    
    Returns:
        OpenAI client instance
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(
            api_key=api_key,
            timeout=float(os.getenv("OPENAI_TIMEOUT", "60.0")),  # 60s default
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
        )
    return _client


def chat_json(system: str, user: str, model: Optional[str] = None):
    """
    Call OpenAI chat completion with retry logic and error handling.
    
    Args:
        system: System message
        user: User message
        model: Model name (defaults to OPENAI_MODEL env var or gpt-4o-mini)
    
    Returns:
        Tuple of (response_text, latency_ms, (tokens_in, tokens_out))
    
    Raises:
        APIError: If all retries fail
    """
    model = model or DEFAULT_MODEL
    t0 = time.time()
    client = _get_client()
    
    try:
        msg = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"}
        )
    except APITimeoutError as e:
        raise APIError(f"OpenAI API timeout after {os.getenv('OPENAI_TIMEOUT', '60')}s: {str(e)}")
    except APIConnectionError as e:
        raise APIError(f"OpenAI API connection error: {str(e)}")
    except APIError as e:
        raise APIError(f"OpenAI API error: {str(e)}")
    
    t1 = time.time()
    text = msg.choices[0].message.content
    usage = getattr(msg, "usage", None)
    tokens_in = usage.prompt_tokens if usage else 0
    tokens_out = usage.completion_tokens if usage else 0
    return text, int(1000 * (t1 - t0)), (tokens_in, tokens_out)
