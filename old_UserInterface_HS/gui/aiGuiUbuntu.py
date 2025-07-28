# aiGuiUbuntu.py
"""
Main GUI for CyberSafe AI Safety Hub
Leverages a custom LLM for Q&A and data analysis.
"""

# ==========
# IMPORTS
# ==========
import importlib
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config as config
import platform
from pathlib import Path

import tkinter as tk
from tkinter import scrolledtext, filedialog
import openai
#==========================
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
#==========================
import ai_functions.llm_client as llm_client
#llm_client.configure()
from utils.io_helpers import export_txt_widget, export_pdf_widget, on_send

from config import (
    # Theme & UI
    BG_COLOR, FG_COLOR, HEADER_BG,
    BUTTON_BG, BUTTON_FG,
    ENTRY_BG, ENTRY_FG,
    TEXT_BG, TEXT_FG,
    FONT_HEADER, FONT_LABEL, FONT_ENTRY, FONT_TEXT,
    ICON_FILENAMES, WINDOW_TITLE,
    # LLM config
    LLM_API_KEY, LLM_BASE_URL, LLM_DEFAULT_MODEL,
    # Paths
    BASE_DIR, IMAGES_DIR,
    # PDF export settings
    PDF_MARGIN_INCH,
    PDF_FONT, PDF_FONT_SIZE, PDF_LINE_SPACING,
)

# ==========
# WINDOW SETUP
# ==========
window = tk.Tk()
window.title(WINDOW_TITLE)
window.configure(bg=BG_COLOR)

# Maximize window
if platform.system() == "Windows":
    window.state("zoomed")
else:
    try:
        window.attributes("-zoomed", True)
    except tk.TclError:
        window.update_idletasks()
        w = window.winfo_screenwidth()
        h = window.winfo_screenheight()
        window.geometry(f"{w}x{h}")

# ==========
# LOAD ICONS
# ==========
icons = {}
for key, path in ICON_FILENAMES.items():
    if path.exists():
        icons[key] = tk.PhotoImage(file=str(path))

# Set window icon if available
if "errorIcon" in icons:
    window.iconphoto(True, icons["errorIcon"])

# ===========
# AI MODES & LOADER
# ===========
# Map friendly mode names to module import paths
AVAILABLE_MODES = {
    "Q&A": "ai_functions.qa",
}
# ===========
# CALL AI FUNCTION
# ===========
def call_ai_function(mode: str, prompt: str) -> str:
    """
    Dynamically import the selected AI mode module and call its run(prompt).
    Returns the response text or an error string.
    """
    module_path = AVAILABLE_MODES.get(mode)
    if not module_path:
        return f"Invalid mode: {mode}"
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        return f"Error importing module '{module_path}': {e}"
    if not hasattr(module, 'run'):
        return f"Module '{module_path}' missing run(prompt) function"
    return module.run(prompt)

# ===========
# HEADER BAR
# ===========
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)
header_frame.pack(fill='x')  # stretch across top
# Label inside header_frame with optional icon
hdr_kwargs = {
    'text': WINDOW_TITLE,
    'font': FONT_HEADER,
    'bg': HEADER_BG,
    'fg': FG_COLOR
}
if 'lockIcon' in icons:
    hdr_kwargs.update(image=icons['lockIcon'], compound='left')

header_label = tk.Label(header_frame, **hdr_kwargs)
header_label.pack()

# ===========
# MODE SELECTOR
# ===========
mode_var = tk.StringVar(value="Q&A")
mode_frame = tk.Frame(window, bg=BG_COLOR)
mode_frame.pack(pady=(10,0))
_ = tk.Label(
    mode_frame, 
    text="AI Mode:", 
    font=FONT_LABEL, 
    bg=BG_COLOR, 
    fg=FG_COLOR).pack(side='left', padx=(20, 5))

mode_menu = tk.OptionMenu(
    mode_frame, 
    mode_var, 
    *AVAILABLE_MODES.keys())
mode_menu.config(
    font=FONT_LABEL, 
    bg=BUTTON_BG, 
    fg=BUTTON_FG, 
    relief="flat", 
    bd=0)
mode_menu.pack(side='left')
# ==========
# LLM MODEL SELECTOR
# ==========
# -------------------------------
llm_model_var = tk.StringVar(value=LLM_DEFAULT_MODEL)
llm_model_frame = tk.Frame(window, bg=BG_COLOR)
llm_model_frame.pack(pady=(10,0))
_ = tk.Label(
    llm_model_frame,
    text="LLM Model:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
).pack(side='left', padx=(20, 5))

llm_menu = tk.OptionMenu (
    llm_model_frame, 
    llm_model_var, 
    LLM_DEFAULT_MODEL)

llm_menu.config(
    font=FONT_LABEL, 
    bg=BUTTON_BG, 
    fg=BUTTON_FG, 
    relief="flat", 
    bd=0)
llm_menu.pack(side='left')
# ===========
# PROMPT ENTRY FIELD
# ===========
prompt_label = tk.Label(
    window, 
    text="Enter AI Prompt:", 
    font=FONT_LABEL, 
    bg=BG_COLOR, 
    fg=FG_COLOR)
prompt_label.pack(anchor='w', padx=20)
#--------------
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=ENTRY_FG,
    relief='flat',
    bd=0
)
question_entry.pack(fill='x', padx=20, pady=(0, 10))
question_entry.focus()


# ===========
# SEND BUTTON
# ===========
send_kwargs = {
    'text': "Send AI Request ▶",
    'font': FONT_LABEL,
    'bg': BUTTON_BG,
    'fg': BUTTON_FG,
    'relief': 'flat',
    'bd': 0,
    'command': on_send
}
#--------------
if 'clockicon' in icons:
    send_kwargs.update(image=icons['clockicon'], compound='left')
# create and place the send button
send_button = tk.Button(window, **send_kwargs)
send_button.pack(pady=(0,10))

# ===========
# OUTPUT AREA
# ===========
output_area = scrolledtext.ScrolledText(
    window,
    wrap=tk.WORD,
    font=FONT_TEXT,
    bg=TEXT_BG,
    fg=TEXT_FG,
    insertbackground=TEXT_FG,
    relief='flat',
    bd=0
)

# ===========
# EXPORT BUTTONS
# ===========
exp_frame = tk.Frame(window, bg=BG_COLOR)
exp_frame.pack(pady=(0, 20))
#--------------
tk.Button(
    exp_frame,
    text="Export as TXT",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    relief='flat',
    bd=0,
    command=lambda: export_txt_widget(output_area)
).pack(side='left', padx=10)

#--------------
tk.Button(
    exp_frame,
    text="Export as PDF",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    relief='flat',
    bd=0,
    command=lambda: export_pdf_widget(output_area)
).pack(side='left', padx=10)

# Now pack the output area so it fills the space below
output_area.pack(fill='both', expand=True, padx=20, pady=(0, 20))
output_area.config(state='disabled')

# ===========
# MAIN LOOP
# ===========
window.mainloop()
