import openai
import sys 
import os 
import httpx
from pathlib import Path
# add project directory to the sys.path for importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import LLM_API_KEY, LLM_BASE_URL, LLM_DEFAULT_MODEL
# Global placeholders for the configured client and default model
_client = None
_default_model = None

class LocalLLM:
    def __init__(self, api_key: str, base_url: str, httpx_client: httpx.Client):
        """
        Initialize the LocalLLM client for the closed system.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.client = httpx_client

    def chat(self, model: str, messages: list, **params):
        """
        Send a chat-completions request using the OpenAI-style endpoint,
        with a messages array of {"role","content"} dicts.
        """
        # Use the exact working endpoint
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": model,
            "messages": messages,
            **params
        }

        # Debug logging
        print("🔍 LLM_POST_URL:   ", url)
        print("🔍 LLM_PAYLOAD:    ", payload)

        try:
            response = self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Log full response body for debugging
            print(f"🔴 LLM API returned {exc.response.status_code}:")
            print(exc.response.text)
            # Propagate a clearer error
            raise RuntimeError(
                f"LLM API error {exc.response.status_code}: {exc.response.text}"
            )

        return response.json()


def configure(
    api_key: str = None,
    base_url: str = None,
    default_model: str = None,
    verify_pem: str = Path(__file__).parent.parent / "lab_ca.pem"
):
    """
    Initialize the global HTTPX client and default model.
    Must be called (via FastAPI startup) before ask().
    """
    from config import LLM_API_KEY, LLM_BASE_URL, LLM_DEFAULT_MODEL
    global _client, _default_model

    _default_model = default_model or LLM_DEFAULT_MODEL

    # Configure timeouts: connect, read, write, pool
    timeout = httpx.Timeout(
        connect=10.0,    # seconds to establish connection
        read=300.0,      # seconds to wait for response data
        write=10.0,      # seconds to send request
        pool=60.0        # seconds to acquire connection from pool
    )

    _client = LocalLLM(
        api_key=api_key or LLM_API_KEY,
        base_url=base_url or LLM_BASE_URL,
        httpx_client=httpx.Client(verify=str(verify_pem), timeout=timeout)
    )


def ask(prompt: str, model: str | None = None, **params) -> str:
    """
    High-level helper: pick the model, build the messages list,
    call LocalLLM.chat(), and extract the assistant's reply.
    """
    if _client is None:
        raise RuntimeError("llm_client is not configured; call configure() first.")

    chosen = model or _default_model
    messages = [{"role": "user", "content": prompt}]

    result = _client.chat(chosen, messages, **params)

    # Extract the assistant’s message content
    return result["choices"][0]["message"]["content"]
