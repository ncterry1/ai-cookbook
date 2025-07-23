# ai_functions/llm_client.py
"""
LLM client module for internal API access.
Provides a configure() to initialize the OpenAI wrapper client,
and ask() (aliased as run) to perform chat completions.
"""


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import (
    LLM_API_KEY, 
    LLM_BASE_URL, 
    LLM_DEFAULT_MODEL, )
from openai import OpenAI
import httpx
from pathlib import Path
import openai
# Module-level state
_client = None
_default_model = None

# ----------
# CONFIGURE CLIENT
# ----------
openai.api_key = LLM_API_KEY
openai.api_base = LLM_BASE_URL

'''
def configure(
    api_key: str = LLM_API_KEY,
    base_url: str = LLM_BASE_URL,
    default_model: str = LLM_DEFAULT_MODEL,
    verify_pem: Path | str = Path(__file__).parent.parent / "lab_ca.pem"
):
    """
    Initialize the internal OpenAI client with API key, base URL, and model.
    Must be called once before using ask()/run().
    """
    global _client, _default_model
    _default_model = default_model
    _client = OpenAI(
        api_key=api_key,
        base_url=base_url.rstrip('/'),
        http_client=httpx.Client(verify=str(verify_pem))
    )
'''
# ----------
# ASK / RUN
# ----------
def ask(prompt: str, model: str = LLM_DEFAULT_MODEL, **params) -> str:
    """
    Send a chat completion request using the configured client.
    Raises RuntimeError if configure() has not been called.
    """
    if _client is None:
        raise RuntimeError("llm_client not configured; call configure() first")

    chosen_model = model or _default_model
    resp = _client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system",
             "content": "Q&A: you are an assistant that obeys instructions exactly. When asked, reply with a healthy, concise answer"},
            {"role": "user", "content": prompt}
        ],
        **params
    )
    return resp.choices[0].message.content

# Alias for dispatcher compatibility
run = ask
