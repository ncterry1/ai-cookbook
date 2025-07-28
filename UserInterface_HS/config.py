import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Closed-system LLM configuration
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_BASE_URL = os.getenv('LLM_BASE_URL')
LLM_DEFAULT_MODEL = os.getenv('LLM_DEFAULT_MODEL')

# List of available models for the dropdown
LLM_MODELS = [
    "openchat-3.5-0106:latest",
    "phi3:latest",
    # Add other local models here
]