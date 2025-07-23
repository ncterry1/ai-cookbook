'''
llm_client.py
High‑level wrapper around the **OpenAI ChatCompletion** endpoint.
This minimal helper exposes a single convenience function, :pyfunc:`ask`,
that accepts a **prompt (str)** and returns the assistant’s textual reply.

Key responsibilities
────────────────────
1. Load authentication & endpoint configuration from :pymod:`config`.
2. Initialise the **`openai`** Python SDK with those credentials.
3. Provide a *thin* pass‑through to ``openai.chat.completions.create`` so that
   the rest of the application can keep OpenAI‑specific code isolated here.
'''

# ════════════════════════════════════════════════════════════════════════════════
# 1) IMPORTS
# ════════════════════════════════════════════════════════════════════════════════
import openai                             # Official OpenAI Python client (pip install openai)
# Pull runtime configuration values from central *config.py* to avoid hard‑coding
# secrets or environment‑specific settings here.
# Need these 3 below to move back one directory to import associated modules
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import (
    OPENAI_API_KEY,                       # Secret API key for authentication
    OPENAI_API_BASE,                      # Base URL (allows pointing to Azure‑OpenAI or proxies)
    OPENAI_DEFAULT_MODEL,                 # Fallback model name (e.g. "gpt-4o-mini")
)

# ════════════════════════════════════════════════════════════════════════════════
# 2) CLIENT INITIALISATION
# ════════════════════════════════════════════════════════════════════════════════
# These assignments configure global *module‑level* variables inside the OpenAI
# SDK.  Subsequent SDK calls inherit these values automatically, so we set them
# once at import‑time.
openai.api_key = OPENAI_API_KEY            # API credential
openai.api_base = OPENAI_API_BASE          # Endpoint root (default is https://api.openai.com)

# ════════════════════════════════════════════════════════════════════════════════
# 3) HIGH‑LEVEL HELPER FUNCTION
# ════════════════════════════════════════════════════════════════════════════════

def ask(prompt: str, model: str = OPENAI_DEFAULT_MODEL, **params) -> str:
    """Submit *prompt* to an LLM and return the assistant’s reply as **str**.

    Parameters
    ----------
    prompt : str
        The user’s question or instruction for the language model.
    model : str, optional
        Identifier of the model to use (default pulled from config).
    **params : dict, optional
        Additional keyword‑arguments are passed verbatim to
        :pyfunc:`openai.chat.completions.create` allowing callers to specify
        advanced options such as *temperature*, *max_tokens*, *stream*, etc.

    Returns
    -------
    str
        The content of the *first* choice returned by the chat completion.
    """
    # Construct and dispatch the request.  The *messages* list must follow the
    # ChatCompletion schema – each item dict includes ``role`` and ``content``.
    # Here we create the minimal conversation with a single **user** turn.
    response = openai.chat.completions.create(
        model=model,                                         # Which LLM to hit
        messages=[{"role": "user", "content": prompt}],    # Conversation history
        **params                                             # Forward any extra params
    )

    # ``response.choices`` is a list (even when we request only one completion).
    # We select index 0, then grab .message.content (the assistant’s text).
    return response.choices[0].message.content
