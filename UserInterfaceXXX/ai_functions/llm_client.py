import openai
import sys
import os

# Add project directory to sys.path for importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_DEFAULT_MODEL

# Initialize OpenAI API with credentials
openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE

def ask(prompt: str, model: str = OPENAI_DEFAULT_MODEL, **params) -> str:
    """Submit prompt to LLM and return response as a string."""
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **params
    )
    return response.choices[0].message.content
