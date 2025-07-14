### llm_client.py
import openai
from HS_config import OPENAI_API_KEY, OPENAI_API_BASE, DEFAULT_MODEL

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE


def ask(prompt: str, model: str = DEFAULT_MODEL, **kwargs) -> str:
    """
    Send a prompt to OpenAI ChatCompletion and return the assistant response.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        **kwargs
    )
    return response.choices[0].message.content