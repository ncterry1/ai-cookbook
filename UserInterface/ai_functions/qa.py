# ----------------------------------------------------------------------------
# Example ai_functions/qa.py (in ai_functions folder)
# ----------------------------------------------------------------------------
"""
ai_functions/qa.py

Basic Q&A mode: calls OpenAI's ChatCompletion API to answer user questions.
"""

# Import the OpenAI client to send API requests
import openai  # Already configured with OPENAI_API_KEY

def run(prompt: str) -> str:
    """
    Run a question-answering prompt against the LLM.

    Args:
        prompt (str): The user question to ask the model.
    Returns:
        str: The model's response text.
    """
    # Build messages for the ChatCompletion endpoint
    messages = [
        {"role": "system", "content": "You are a helpful cybersecurity assistant."},
        {"role": "user",   "content": prompt},
    ]
    # Send the request to OpenAI and get a response
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Model selection
        messages=messages,
        temperature=0.5,        # Controls randomness: 0.0 = deterministic
        max_tokens=512,         # Maximum tokens in the reply
    )
    # Extract and return the text content of the first choice
    return response.choices[0].message.content.strip()