import os
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

# Cache client globally so we don't re-instantiate it on every request
_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            logger.warning("GROQ_API_KEY is missing! Using mock responses.")
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def invoke_groq(prompt: str, model: str = "llama-3.3-70b-versatile", response_format=None, fallback: str = "{}") -> str:
    """Invokes Groq API with the given prompt."""
    client = get_groq_client()
    if not client:
        return fallback
    
    try:
        kwargs = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "model": model,
            "temperature": 0.2, # Keep it deterministic 
        }
        
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}
            
        chat_completion = client.chat.completions.create(**kwargs)
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return fallback
