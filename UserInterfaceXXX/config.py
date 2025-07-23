# config.py

import os
from dotenv import load_dotenv

# Load variables from .env in the project root
load_dotenv()

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4")

# Sanity check
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in your environment")
