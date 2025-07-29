import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import openai
from config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_DEFAULT_MODEL

openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_API_BASE

def ask_llm(prompt, model=None):
    if model is None:
        model = OPENAI_DEFAULT_MODEL

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
