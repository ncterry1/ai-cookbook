### aiGuiUbuntu.py

"""
Main GUI for CyberSafe AI Safety Hub
Leverages OpenAI API for Q&A.
"""

# ==========
# IMPORTS
# ==========
import importlib
import config
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext
import platform
from ai_functions.llm_client import ask
from utils.io_helpers import export_txt_widget, export_pdf_widget

# Force reload config for interactive scenarios
importlib.reload(config)

from config import (
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
AVAILABLE_MODES = {
    "Q&A": "ai_functions.llm_client",
    # add additional modes as needed
}
# ========================================
def call_ai_function(mode: str, prompt: str) -> str:
    """
    Dynamically load the module for the selected mode and invoke its ask() or run() function.
    """
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
# ==========
# MODE SELECTOR
# ==========
mode_var = tk.StringVar(value='Q&A')
mode_frame = tk.Frame(window, bg=BG_COLOR)
mode_frame.pack(pady=(10, 0))
mode_label = tk.Label(
    mode_frame,
    text="AI Mode:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)
mode_label.pack(side='left', padx=(20,5))
mode_menu = tk.OptionMenu(mode_frame, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    relief='flat',
    bd=0
)
mode_menu.pack(side='left')
# ==========
# PROMPT ENTRY FIELD
# ==========
prompt_label = tk.Label(
    window,
    text="Enter AI Prompt:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)
prompt_label.pack(anchor='w', padx=20)
# ========================================
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
# SEND BUTTON CALLBACK
# ==========
def on_send():
    user_prompt = question_entry.get().strip()
    if not user_prompt:
        return

    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    placeholder = f"🔍 AI Prompt:\n{user_prompt}\n\n⏳ Thinking..."
    output_area.insert(tk.END, placeholder)
    output_area.config(state='disabled')
    window.update_idletasks()

    try:
        ai_result = ask(user_prompt)
    except Exception as e:
        ai_result = f"❌ Error: {e}"

    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, ai_result)
    output_area.config(state='disabled')
# ========================================
# ==========
# SEND BUTTON
# ==========
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