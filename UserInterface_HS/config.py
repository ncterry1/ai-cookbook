# config.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter   # provides a (width, height) tuple
# ============================================
# ===========
# 1) ENV & LLM CONFIG
# ============================================
load_dotenv(Path(__file__).parent / ".env")

LLM_API_KEY       = os.getenv("LLM_API_KEY")
LLM_BASE_URL      = os.getenv("LLM_BASE_URL")
LLM_DEFAULT_MODEL = os.getenv("LLM_DEFAULT_MODEL")
# ============================================
if not (LLM_API_KEY and LLM_BASE_URL and LLM_DEFAULT_MODEL):
    raise ValueError(
        "Please set LLM_API_KEY, LLM_BASE_URL, and LLM_DEFAULT_MODEL in your .env"
    )
# ============================================
# ============================================
# For if a user has more than one model to send AI request to
# This is a sample and not complete for HS
#LLM_MODELS = [
#    "gpt-3.5-turbo",
#    "gpt-4",
#    "Llama-4-Scout-17B-16E-Instruct:latest",
#    "llama (not complte)",
#    "Mistral (not complete)",
#    "gemma-2 (not complete)"
#]
# ============================================
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
