### aiGuiUbuntu.py

"""
Main GUI for CyberSafe AI Safety Hub
Leverages OpenAI API for Q&A.
"""

# ==========
# IMPORTS
# ==========
import importlib
import UserInterface_LS.config.config as config
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext
import platform
from ai_functions.llm_client import ask
from utils.io_helpers import export_txt_widget, export_pdf_widget

# Force reload config for interactive scenarios
importlib.reload(config)

from UserInterface_LS.config.config import (
    # Theme & UI
    BG_COLOR, FG_COLOR, HEADER_BG,
    BUTTON_BG, BUTTON_FG,
    ENTRY_BG, ENTRY_FG,
    TEXT_BG, TEXT_FG,
    FONT_HEADER, FONT_LABEL, FONT_ENTRY, FONT_TEXT,
    ICON_FILENAMES, WINDOW_TITLE,
    # LLM config
    OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_DEFAULT_MODEL,
    # Paths
    BASE_DIR, IMAGES_DIR,
    # PDF export settings
    PDF_PAGE_HEIGHT, PDF_PAGE_WIDTH, PDF_MARGIN_INCH,
    PDF_FONT, PDF_FONT_SIZE, PDF_LINE_SPACING,
    # Import the array of gpt-llm-models to choose from
    LLM_MODELS
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
default_icon = icons.get('llmicon') or icons.get('noActionicon')
if default_icon:
    window.iconphoto(True, default_icon)
# ========================================
# ========================================
# ========================================
# AI MODES & LOADER
# ========================================
# Options to let user choose the focus of the llm
from UserInterface_LS.config.config import AVAILABLE_MODES
def call_ai_function(mode: str, prompt: str) -> str:
    # Dynamically load the module for the selected mode and invoke its ask() or run() function.
    module_path = AVAILABLE_MODES.get(mode)
    if not module_path:
        return f"Invalid mode: {mode}"
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        return f"Error importing module '{module_path}': {e}"
    # Prefer run(), fallback to ask()
    if hasattr(module, 'run'):
        return module.run(prompt)
    if hasattr(module, 'ask'):
        return module.ask(prompt)
    return f"Module '{module_path}' has no run() or ask() function"
# ========================================
# ========================================
# ========================================
# HEADER BAR
# ========================================
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)
header_frame.pack(fill='x')
hdr_kwargs = {
    'text': WINDOW_TITLE,
    'font': FONT_HEADER,
    'bg': HEADER_BG,
    'fg': FG_COLOR
}
if 'llmicon' in icons:
    hdr_kwargs.update(image=icons['llmicon'], compound='left')
header_label = tk.Label(header_frame, **hdr_kwargs)
header_label.pack()
# ========================================
# ========================================
# ==========
# MODE SELECTOR
# # The top dropdown that lets a user select which focus they want the llm to have
mode_var = tk.StringVar(value='Q&A')
mode_frame = tk.Frame(window, bg=BG_COLOR)
mode_frame.pack(pady=(10, 0))
mode_label = tk.Label(
    mode_frame,
    text="AI Mode:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
).pack(side='left', padx=(30,5))
mode_menu = tk.OptionMenu(mode_frame, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG, relief='flat', bd=0)
mode_menu.pack(side='left')
# ========================================
# ========================================
# LLM Selector (gpt-3.5-turbo, gpt-4)
# Label / dropdown to choose which llm to use
llm_model_var = tk.StringVar(value=OPENAI_DEFAULT_MODEL)
llm_model_frame = tk.Frame(window, bg=BG_COLOR)
llm_model_frame.pack(pady=(10, 0))
llm_model_label = tk.Label(
    llm_model_frame,
    text="LLM Model:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR,
    ).pack(side='left', padx=(20,5))

llm_menu = tk.OptionMenu(llm_model_frame, llm_model_var, *LLM_MODELS)
llm_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", bd=0)
llm_menu.pack(side='left')
# ========================================
# ==========
# PROMPT ENTRY FIELD
# The text right above the user input line for asking llm a question
prompt_label = tk.Label(
    window,
    text="Enter AI Prompt:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)
prompt_label.pack(anchor='w', padx=20)
# ========================================
# input line for user to ask question
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=ENTRY_FG,
    relief='flat',
    bd=0
)
# ========================================
question_entry.pack(fill='x', padx=20, pady=(0, 10))
question_entry.focus()
# ========================================
# ==========
# SEND BUTTON
# ==========
from utils.io_helpers import on_send
send_kwargs = {
    'text': "Send AI Request ▶",
    'font': FONT_LABEL,
    'bg': BUTTON_BG,
    'fg': BUTTON_FG,
    'relief': 'flat',
    'bd': 0,
    'command': on_send
}
# ========================================
if 'clockicon' in icons:
    send_kwargs.update(image=icons['clockicon'], compound='left')
send_button = tk.Button(window, **send_kwargs)
send_button.pack(pady=(0, 10))
# ========================================
# ==========
# OUTPUT AREA
# ==========
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
# ========================================
output_area.config(state='disabled')
output_area.pack(fill='both', expand=True, padx=20, pady=(0, 20))
# ========================================
# ==========
# EXPORT BUTTONS
# ==========
exp_frame = tk.Frame(window, bg=BG_COLOR)
exp_frame.pack(pady=(0, 20))
# ========================================
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
# ========================================
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
# ========================================
# ==========
# MAIN LOOP
# ==========
window.mainloop()
# ========================================
# ========================================
# ========================================