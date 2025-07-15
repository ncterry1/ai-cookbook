# config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter   # provides a (width, height) tuple

# ===========
# 1) ENV & LLM CONFIG
# ===========
load_dotenv(Path(__file__).parent / ".env")

OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE      = os.getenv("OPENAI_API_BASE")
OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL")

if not (OPENAI_API_KEY and OPENAI_API_BASE and OPENAI_DEFAULT_MODEL):
    raise ValueError(
        "Please set OPENAI_API_KEY, OPENAI_API_BASE, and OPENAI_DEFAULT_MODEL in your .env"
    )
# ============================================
# We have calling functions to the llms to tell them to focus 
# QA on llm_client is a general assistant fof general questions. 
AVAILABLE_MODES = {
    "Q&A":           "ai_functions.llm_client",
    "Data Analysis": "ai_functions.data_analysis",
    # add more modes here as you build them
}
# ============================================
# For if a user has more than one model to send AI request to
# This is a sample and not complete for HS
LLM_MODELS = [
    "gpt-3.5-turbo",
    "gpt-4"
]
# ===========
# 2) THEME COLORS & FONTS
# ===========
BG_COLOR   = "#2E3440"
FG_COLOR   = "#ECEFF4"
HEADER_BG  = "#4C566A"
BUTTON_BG  = "#5E81AC"
BUTTON_FG  = "#ECEFF4"
ENTRY_BG   = "#D3D3D3"
ENTRY_FG   = "#000000"
TEXT_BG    = "#D3D3D3"
TEXT_FG    = "#000000"

FONT_HEADER = ("TkDefaultFont", 18, "bold")
FONT_LABEL  = ("TkDefaultFont", 14)
FONT_ENTRY  = ("TkDefaultFont", 14)
FONT_TEXT   = ("TkDefaultFont", 12)

# ===========
# 3) ICON & RESOURCE PATHS
# ===========
BASE_DIR       = Path(__file__).parent
IMAGES_DIR     = BASE_DIR / "images"
ICON_FILENAMES = {
    "noActionicon": IMAGES_DIR / "noActionicon.png",
    "clockicon":    IMAGES_DIR / "clockicon.png",
    "llmicon":      IMAGES_DIR / "llmicon.png",
}

# ===========
# 4) VENV & PDF EXPORT SETTINGS
# ===========
DEFAULT_VENV      = ".venv"

# actual page dimensions from reportlab
PDF_PAGE_WIDTH    = letter[0]
PDF_PAGE_HEIGHT   = letter[1]
PDF_MARGIN_INCH   = 1         # margin in inches
PDF_FONT          = "Courier"
PDF_FONT_SIZE     = 12
PDF_LINE_SPACING  = 1.2       # leading = FONT_SIZE * LINE_SPACING

# ===========
# 5) OTHER GLOBALS
# ===========
WINDOW_TITLE = "CyberSafe AI Safety Hub"
