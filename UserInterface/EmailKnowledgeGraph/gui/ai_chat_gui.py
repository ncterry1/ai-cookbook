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

# **************************************************************************
# Standard library imports
# **************************************************************************
import os                  # Access environment variables
import importlib           # Dynamically import modules at runtime

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
BG_COLOR     = "#2E3440"  # Window background (dark slate)
FG_COLOR     = "#ECEFF4"  # Default text (off-white)
HEADER_BG    = "#4C566A"  # Header background (muted gray-blue)
BUTTON_BG    = "#5E81AC"  # Button background (steel blue)
BUTTON_FG    = "#ECEFF4"  # Button text (off-white)
ENTRY_BG     = "#D3D3D3"  # Entry background (light gray)
ENTRY_FG     = "#000000"  # Entry text (black)
TEXT_BG      = "#D3D3D3"  # Output background (light gray)
TEXT_FG      = "#000000"  # Output text (black)
FONT_HEADER  = ("Consolas", 18, "bold")  # Header font
FONT_LABEL   = ("Consolas", 14)            # Labels font
FONT_ENTRY   = ("Consolas", 14)            # Entry font
FONT_TEXT    = ("Consolas", 12)            # Text area font

# **************************************************************************
# Input/Output Limits
# **************************************************************************
# Model context window (~4096 tokens for gpt-3.5-turbo)
# `max_tokens` caps output length
# Large inputs may need chunking
# ScrolledText widget may slow with very large text

# **************************************************************************
# 1. Configure OpenAI API key
# **************************************************************************
openai.api_key = os.getenv("OPENAI_API_KEY")  # Load API key
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# **************************************************************************
# 2. Define available AI modes and dynamic loader
# **************************************************************************
AVAILABLE_MODES = {
    "Q&A":           "ai_functions.qa",            # Module for Q&A mode
    "Data Analysis": "ai_functions.data_analysis", # Module for Data Analysis mode
}

def call_ai_function(mode, prompt):
    module_name = AVAILABLE_MODES.get(mode)
    if not module_name:
        raise ValueError(f"Unknown mode: {mode}")
    module = importlib.import_module(module_name)      # Dynamically import module
    if not hasattr(module, "run"):
        raise AttributeError(f"Module '{module_name}' missing run(prompt)")
    return module.run(prompt)                          # Execute run() and return result

# **************************************************************************
# 3. Export functions
# **************************************************************************
def export_txt():
    """
    Export the contents of the output_area as a .txt file.
    """
    text = output_area.get("1.0", tk.END)
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*")]
    )
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def export_pdf():
    """
    Export the contents of the output_area as a .pdf file (with 1" margins and proper text wrapping).
    """
    text = output_area.get("1.0", tk.END)
    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*")]
    )
    if path:
        # Create PDF canvas with letter size (8.5" x 11" -> 612 x 792 points)
        page_width, page_height = letter
        c = canvas.Canvas(path, pagesize=letter)
        # Set margins: 1 inch = 72 points
        left_margin = 72
        right_margin = page_width - 72
        top_margin = page_height - 72
        bottom_margin = 72
        # Initialize text object
        text_obj = c.beginText()
        text_obj.setTextOrigin(left_margin, top_margin)
        # Use a monospaced font for consistent wrapping
        font_name = 'Courier'
        font_size = 12
        text_obj.setFont(font_name, font_size)
        text_obj.setLeading(font_size * 1.2)  # Line spacing
        # Calculate wrap width based on printable area and actual char width
        printable_width = right_margin - left_margin
        avg_char_width = c.stringWidth('M', font_name, font_size)
        wrap_width = int(printable_width / avg_char_width)
        import textwrap
        for line in text.splitlines():
            wrapped_lines = textwrap.wrap(line, width=wrap_width) or ['']
            for wl in wrapped_lines:
                # Start new page if below bottom margin
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

# 4. Handle Send action (must be defined before UI references it)
# **************************************************************************
def on_send():
    prompt = question_entry.get().strip()              # Get user input from entry
    if not prompt:
        return                                        # Do nothing if entry is empty
    # Display placeholder while waiting
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(
        tk.END,
        f"🔍 {mode_var.get()} Prompt:\n{prompt}\n\n⏳ Thinking…\n"
    )
    output_area.config(state='disabled')
    window.update_idletasks()
    # Call AI function and display result
    try:
        response = call_ai_function(mode_var.get(), prompt)
    except Exception as e:
        response = f"❌ Error: {e}"
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, response)
    output_area.config(state='disabled')

# **************************************************************************
# 5. Build the Tkinter UI (maximized with title bar)
# **************************************************************************
window = tk.Tk()                                    # Main application window
window.title("🔒 Cybersecurity AI Chat")           # Window title bar text
window.state('zoomed')                              # Start maximized
window.configure(bg=BG_COLOR)                       # Set window background color
window.bind('<Escape>', lambda e: window.state('normal'))  # Exit maximize on Esc

# **************************************************************************
# Header
# **************************************************************************
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)  # Container for header
header_frame.pack(fill='x')                            # Stretch across width
Label_header = tk.Label(
    header_frame,
    text="🔒 Cybersecurity AI Chat Interface",
    font=FONT_HEADER,
    bg=HEADER_BG,
    fg=FG_COLOR
)                                                     # Title label widget
Label_header.pack()                                    # Place label

# **************************************************************************
# Mode selector
# **************************************************************************
Label_mode = tk.Label(
    window,
    text="Mode:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)                                                     # Label for dropdown menu
Label_mode.pack(pady=(10,5))                          # Vertical padding
mode_var = tk.StringVar(value="Q&A")                 # Track selected mode
mode_menu = tk.OptionMenu(window, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG)  # Style combo
mode_menu.pack(pady=(0,10))                            # Place dropdown

# **************************************************************************
# Prompt input
# **************************************************************************
Label_prompt = tk.Label(
    window,
    text="Enter prompt:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)                                                     # Label above input field
Label_prompt.pack(anchor='w', padx=20, pady=(0,5))      # Left-align label
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=ENTRY_FG,
    relief='flat',
    bd=5
)                                                     # Single-line entry widget
question_entry.pack(fill='x', padx=20, pady=(0,10))   # Expand horizontally
question_entry.focus()                                 # Focus on start

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
)                                                     # Button to submit prompt
send_button.pack(pady=(0,10))                          # Padding below button
# Frame for export buttons
export_frame = tk.Frame(window, bg=BG_COLOR)
export_frame.pack(pady=(0,20))                         # Space below frame
# Export as TXT button
export_txt_button = tk.Button(
    export_frame,
    text="Export as TXT",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    command=export_txt
)
export_txt_button.pack(side='left', padx=10)
# Export as PDF button
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
)                                                     # Multi-line, scrollable text area
output_area.pack(fill='both', expand=True, padx=20, pady=(0,20))
output_area.config(state='disabled')                   # Initialize as read-only

# **************************************************************************
# 6. Start GUI event loop
# **************************************************************************
window.mainloop()                                     # Enter Tkinter event loop