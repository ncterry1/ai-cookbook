"""
ai_chat_gui.py

A sleek, cybersecurity-themed maximized desktop GUI that supports multiple AI functions
from separate scripts in the `ai_functions` package, with export-to-TXT and export-to-PDF features.
-------------------------------------------------------------------------------
INSTALLATION NOTES:
  • Requires the OpenAI Python client >=1.0.0:
      pip install --upgrade openai
  • Requires ReportLab for PDF export:
      pip install reportlab
  • Tkinter is part of the Python standard library on most platforms.
    If you get an ImportError on tkinter:
      • Debian/Ubuntu: sudo apt install python3-tk
      • Fedora:        sudo dnf install python3-tkinter
      • Windows/macOS: normally included with your Python installer.
  • Ensure you have an `ai_functions` folder with at least `qa.py` and `data_analysis.py`:
      mkdir ai_functions
  • Set your API key in your environment before running:
      export OPENAI_API_KEY="your_api_key_here"   # macOS/Linux
      set OPENAI_API_KEY="your_api_key_here"      # Windows PowerShell
-------------------------------------------------------------------------------
"""
from dotenv import load_dotenv
from pathlib import Path

# Load the .env file in your project root
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# **************************************************************************
# Standard library imports
# **************************************************************************
import os                  # Access environment variables
import importlib           # Dynamically import modules at runtime
import platform            # Detect OS for compatibility handling

# **************************************************************************
# External library imports
# **************************************************************************
import openai              # OpenAI client library (>=1.0.0 interface)
from reportlab.lib.pagesizes import letter  # PDF page size
from reportlab.pdfgen import canvas         # PDF generation

# **************************************************************************
# GUI library imports
# **************************************************************************
import tkinter as tk                       # Core Tkinter functionality
from tkinter import scrolledtext           # ScrolledText widget for output area
from tkinter import filedialog              # File dialogs for saving exports

# **************************************************************************
# Color & Font Theme (Nord-Inspired with light inputs)
# **************************************************************************
BG_COLOR     = "#2E3440"
FG_COLOR     = "#ECEFF4"
HEADER_BG    = "#4C566A"
BUTTON_BG    = "#5E81AC"
BUTTON_FG    = "#ECEFF4"
ENTRY_BG     = "#D3D3D3"
ENTRY_FG     = "#000000"
TEXT_BG      = "#D3D3D3"
TEXT_FG      = "#000000"
FONT_HEADER  = ("Consolas", 18, "bold")
FONT_LABEL   = ("Consolas", 14)
FONT_ENTRY   = ("Consolas", 14)
FONT_TEXT    = ("Consolas", 12)

# **************************************************************************
# 1. Configure OpenAI API key
# **************************************************************************
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# **************************************************************************
# 2. Define available AI modes and dynamic loader
# **************************************************************************
AVAILABLE_MODES = {
    "Q&A":           "ai_functions.qa",
    "Data Analysis": "ai_functions.data_analysis",
}

def call_ai_function(mode, prompt):
    module_name = AVAILABLE_MODES.get(mode)
    if not module_name:
        raise ValueError(f"Unknown mode: {mode}")
    module = importlib.import_module(module_name)
    if not hasattr(module, "run"):
        raise AttributeError(f"Module '{module_name}' missing run(prompt)")
    return module.run(prompt)

# **************************************************************************
# 3. Export functions
# **************************************************************************
def export_txt():
    text = output_area.get("1.0", tk.END)
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*")]
    )
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

def export_pdf():
    text = output_area.get("1.0", tk.END)
    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*")]
    )
    if path:
        page_width, page_height = letter
        c = canvas.Canvas(path, pagesize=letter)
        left_margin = 72
        right_margin = page_width - 72
        top_margin = page_height - 72
        bottom_margin = 72
        text_obj = c.beginText()
        text_obj.setTextOrigin(left_margin, top_margin)
        font_name = 'Courier'
        font_size = 12
        text_obj.setFont(font_name, font_size)
        text_obj.setLeading(font_size * 1.2)
        printable_width = right_margin - left_margin
        avg_char_width = c.stringWidth('M', font_name, font_size)
        wrap_width = int(printable_width / avg_char_width)
        import textwrap
        for line in text.splitlines():
            wrapped_lines = textwrap.wrap(line, width=wrap_width) or ['']
            for wl in wrapped_lines:
                if text_obj.getY() <= bottom_margin:
                    c.drawText(text_obj)
                    c.showPage()
                    text_obj = c.beginText()
                    text_obj.setTextOrigin(left_margin, top_margin)
                    text_obj.setFont(font_name, font_size)
                    text_obj.setLeading(font_size * 1.2)
                text_obj.textLine(wl)
        c.drawText(text_obj)
        c.save()

# **************************************************************************
# 4. Handle Send action
# **************************************************************************
def on_send():
    prompt = question_entry.get().strip()
    if not prompt:
        return
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(
        tk.END,
        f"🔍 {mode_var.get()} Prompt:\n{prompt}\n\n⏳ Thinking…\n"
    )
    output_area.config(state='disabled')
    window.update_idletasks()
    try:
        response = call_ai_function(mode_var.get(), prompt)
    except Exception as e:
        response = f"❌ Error: {e}"
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, response)
    output_area.config(state='disabled')

# **************************************************************************
# 5. Build the Tkinter UI (cross-platform maximized window)
# **************************************************************************
window = tk.Tk()
window.title("🔒 Cybersecurity AI Chat")

# Cross-platform maximize support
if platform.system() == 'Windows':
    window.state('zoomed')  # Windows only
else:
    try:
        window.attributes('-zoomed', True)  # Most Linux window managers
    except tk.TclError:
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(f"{screen_width}x{screen_height}+0+0")

window.configure(bg=BG_COLOR)

# Escape key behavior: Windows only
if platform.system() == 'Windows':
    window.bind('<Escape>', lambda e: window.state('normal'))

# **************************************************************************
# Header
# **************************************************************************
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)
header_frame.pack(fill='x')
Label_header = tk.Label(
    header_frame,
    text="🔒 Cybersecurity AI Chat Interface",
    font=FONT_HEADER,
    bg=HEADER_BG,
    fg=FG_COLOR
)
Label_header.pack()

# **************************************************************************
# Mode selector
# **************************************************************************
Label_mode = tk.Label(
    window,
    text="Mode:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)
Label_mode.pack(pady=(10,5))
mode_var = tk.StringVar(value="Q&A")
mode_menu = tk.OptionMenu(window, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG)
mode_menu.pack(pady=(0,10))

# **************************************************************************
# Prompt input
# **************************************************************************
Label_prompt = tk.Label(
    window,
    text="Enter prompt:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)
Label_prompt.pack(anchor='w', padx=20, pady=(0,5))
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=ENTRY_FG,
    relief='flat',
    bd=5
)
question_entry.pack(fill='x', padx=20, pady=(0,10))
question_entry.focus()

# **************************************************************************
# Send & Export Buttons
# **************************************************************************
send_button = tk.Button(
    window,
    text="Send ▶",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    command=on_send
)
send_button.pack(pady=(0,10))

export_frame = tk.Frame(window, bg=BG_COLOR)
export_frame.pack(pady=(0,20))

export_txt_button = tk.Button(
    export_frame,
    text="Export as TXT",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    command=export_txt
)
export_txt_button.pack(side='left', padx=10)

export_pdf_button = tk.Button(
    export_frame,
    text="Export as PDF",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    command=export_pdf
)
export_pdf_button.pack(side='left', padx=10)

# **************************************************************************
# Output area
# **************************************************************************
output_area = scrolledtext.ScrolledText(
    window,
    wrap=tk.WORD,
    font=FONT_TEXT,
    bg=TEXT_BG,
    fg=TEXT_FG,
    insertbackground=TEXT_FG,
    relief='flat',
    bd=5
)
output_area.pack(fill='both', expand=True, padx=20, pady=(0,20))
output_area.config(state='disabled')

# **************************************************************************
# 6. Start GUI event loop
# **************************************************************************
window.mainloop()
