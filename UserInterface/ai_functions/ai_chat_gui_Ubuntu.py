"""
ai_chat_gui_Ubuntu.py

A robust, cybersecurity-themed maximized GUI for Ubuntu/Linux and Windows,
leveraging OpenAI for AI-driven Q&A and data analysis. Exports to text and PDF.
Loads external icons (lock and hourglass) at runtime; richly commented for learning.

Installation & Usage:
  1. Python 3.8+ recommended
  2. Create and activate a virtualenv:
       python3 -m venv .venv
       source .venv/bin/activate
  3. Install dependencies:
       pip install --upgrade openai reportlab python-dotenv
  4. (Optional) Store your API key in a .env file at project root:
       OPENAI_API_KEY="sk-..."
     Uncomment dotenv lines below to load automatically.
  5. Place lock_icon.png and hourglass_icon.png alongside this script.
  6. Run:
       python ai_chat_gui_Ubuntu.py
"""

# --------------------------------------------------
# 1) IMPORT STANDARD LIBRARIES
# --------------------------------------------------
import os                       # For environment variables and file operations
import importlib                # To dynamically import AI mode modules by name
import platform                 # To detect OS for maximize/fullscreen logic
from pathlib import Path        # For easy and robust filesystem path manipulations

# --------------------------------------------------
# 2) IMPORT EXTERNAL LIBRARIES
# --------------------------------------------------
import openai                   # OpenAI API client library
from reportlab.lib.pagesizes import letter  # Standard letter-size for PDF
from reportlab.pdfgen import canvas         # Canvas class for PDF generation

# --------------------------------------------------
# 3) IMPORT TKINTER FOR GUI
# --------------------------------------------------
import tkinter as tk            # Core Tkinter functionality
from tkinter import scrolledtext, filedialog  # Widgets: ScrolledText & FileDialog

# --------------------------------------------------
# 4) DEFINE THEME CONSTANTS
# --------------------------------------------------
# Colors are Nord-inspired: dark backgrounds with light text accents
BG_COLOR     = "#2E3440"       # Main window background color
FG_COLOR     = "#ECEFF4"       # Primary foreground (text) color
HEADER_BG    = "#4C566A"       # Header bar background color
BUTTON_BG    = "#5E81AC"       # Buttons background color
BUTTON_FG    = "#ECEFF4"       # Buttons text color
ENTRY_BG     = "#D3D3D3"       # Entry field background (light gray)
ENTRY_FG     = "#000000"       # Entry field text color (black)
TEXT_BG      = "#D3D3D3"       # Output text area background
TEXT_FG      = "#000000"       # Output text area text color
# Use system default font for modern consistency
FONT_HEADER  = ("TkDefaultFont", 18, "bold")  # Header text font
FONT_LABEL   = ("TkDefaultFont", 14)           # Labels for inputs/buttons
FONT_ENTRY   = ("TkDefaultFont", 14)           # Entry field font
FONT_TEXT    = ("TkDefaultFont", 12)           # Output text area font

# --------------------------------------------------
# 5) CONFIGURE OPENAI API KEY
# --------------------------------------------------
# Optionally load from .env file by uncommenting below:
# from dotenv import load_dotenv
# load_dotenv(dotenv_path=Path(__file__).parent / '.env')
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    # Halt execution if API key is missing
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# --------------------------------------------------
# 6) DEFINE AI MODES & LOADER
# --------------------------------------------------
# Map friendly mode names to Python module import paths
AVAILABLE_MODES = {
    "Q&A":           "ai_functions.qa",
    "Data Analysis": "ai_functions.data_analysis"
}

def call_ai_function(mode: str, prompt: str) -> str:
    """
    Dynamically import the selected AI mode module and call its run(prompt).
    Returns the response text, or an error string.
    """
    module_path = AVAILABLE_MODES.get(mode)
    if not module_path:
        return f"Invalid mode: {mode}"  # Mode not recognized
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        return f"Error importing module '{module_path}': {e}"
    if not hasattr(module, 'run'):
        return f"Module '{module_path}' missing run(prompt) function"
    # Execute the AI function and return its result
    return module.run(prompt)

# --------------------------------------------------
# 7) EXPORT FUNCTIONS: TXT & PDF
# --------------------------------------------------
def export_txt() -> None:
    """
    Export current output text to a .txt file via a save dialog.
    """
    text_content = output_area.get("1.0", tk.END)  # Get all text
    save_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*")]
    )
    if save_path:
        # Write text in UTF-8 to preserve special characters
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(text_content)


def export_pdf() -> None:
    """
    Export current output text to a word-wrapped PDF with 1-inch margins.
    """
    text_content = output_area.get("1.0", tk.END)
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*")]
    )
    if not save_path:
        return  # User canceled
    # Initialize PDF canvas
    pdf = canvas.Canvas(save_path, pagesize=letter)
    left_margin, bottom_margin = 72, 72  # 1 inch margins = 72 points
    page_width, page_height = letter
    right_margin = page_width - 72
    top_margin = page_height - 72
    # Begin a text object at top-left
    text_obj = pdf.beginText(left_margin, top_margin)
    text_obj.setFont('Courier', 12)  # Monospaced font for uniform wrapping
    text_obj.setLeading(14.4)        # Line spacing = 1.2 * font size
    # Calculate wrap width in characters
    wrap_width = int((right_margin - left_margin) / pdf.stringWidth('M', 'Courier', 12))
    import textwrap
    for line in text_content.splitlines():
        # Wrap long lines
        for segment in textwrap.wrap(line, width=wrap_width) or ['']:
            # If out of vertical space, start a new page
            if text_obj.getY() <= bottom_margin:
                pdf.drawText(text_obj)
                pdf.showPage()
                text_obj = pdf.beginText(left_margin, top_margin)
                text_obj.setFont('Courier', 12)
                text_obj.setLeading(14.4)
            text_obj.textLine(segment)
    # Draw and save
    pdf.drawText(text_obj)
    pdf.save()

# --------------------------------------------------
# 8) SEND BUTTON CALLBACK
# --------------------------------------------------
def on_send() -> None:
    """
    Triggered by the "Send AI Request" button or Enter key:
      1. Read prompt
      2. Show placeholder with hourglass icon text
      3. Call AI and display response
    """
    user_prompt = question_entry.get().strip()
    if not user_prompt:
        return  # Ignore empty
    # Display placeholder
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    placeholder_text = f"🔍 {mode_var.get()} AI Prompt:\n{user_prompt}\n\n⏳ Thinking..."
    output_area.insert(tk.END, placeholder_text)
    output_area.config(state='disabled')
    window.update_idletasks()  # Force refresh
    # Call AI
    try:
        ai_result = call_ai_function(mode_var.get(), user_prompt)
    except Exception as err:
        ai_result = f"❌ Error: {err}"
    # Display AI response
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, ai_result)
    output_area.config(state='disabled')

# --------------------------------------------------
# 9) BUILD & LAYOUT THE GUI
# --------------------------------------------------
# Create main window
window = tk.Tk()
# Load icons from external files at runtime
icons = {}
for icon_name in ('lock_icon.png', 'hourglass_icon.png'):
    icon_path = Path(__file__).parent / icon_name
    if icon_path.exists():
        # Store PhotoImage in dict to prevent garbage collection
        icons[icon_name] = tk.PhotoImage(file=str(icon_path))
# Set window icon (appears in title bar) if lock icon loaded
if 'lock_icon.png' in icons:
    window.iconphoto(True, icons['lock_icon.png'])
# Set window title text only (icon handled separately)
window.title("CyberSafe AI Safety Hub")
# Maximize window with title bar intact
if platform.system() == 'Windows':
    window.state('zoomed')  # Windows-specific maximize
else:
    try:
        window.attributes('-zoomed', True)  # Linux maximize supported WMs
    except tk.TclError:
        # Fallback: manual full-screen geometry
        window.update_idletasks()
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry(f"{w}x{h}+0+0")
# Apply background color
window.configure(bg=BG_COLOR)

# Header frame and label
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)
header_frame.pack(fill='x')  # Stretch across top
# Label inside header_frame with optional lock icon
hdr_kwargs = { 'text': "CyberSafe AI Safety Hub", 'font': FONT_HEADER,
               'bg': HEADER_BG, 'fg': FG_COLOR }
if 'lock_icon.png' in icons:
    hdr_kwargs.update(image=icons['lock_icon.png'], compound='left')
header_label = tk.Label(header_frame, **hdr_kwargs)
header_label.pack()

# Mode selector label & dropdown
mode_label = tk.Label(window, text="AI Mode:", font=FONT_LABEL,
                      bg=BG_COLOR, fg=FG_COLOR)
mode_label.pack(pady=(10, 5))
mode_var = tk.StringVar(value="Q&A")
mode_menu = tk.OptionMenu(window, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG,
                 relief='flat', bd=0)
mode_menu.pack(pady=(0, 10))

# AI Prompt entry label & field
prompt_label = tk.Label(window, text="Enter AI Prompt:",
                        font=FONT_LABEL, bg=BG_COLOR, fg=FG_COLOR)
prompt_label.pack(anchor='w', padx=20)
question_entry = tk.Entry(window, font=FONT_ENTRY, bg=ENTRY_BG,
                          fg=ENTRY_FG, insertbackground=ENTRY_FG,
                          relief='flat', bd=0)
question_entry.pack(fill='x', padx=20, pady=(0,10))
question_entry.focus()  # Focus text cursor on entry

# Send AI Request button
send_kwargs = { 'text': "Send AI Request ▶", 'font': FONT_LABEL,
                'bg': BUTTON_BG, 'fg': BUTTON_FG,
                'relief': 'flat', 'bd': 0,
                'command': on_send }
if 'lock_icon.png' in icons:
    send_kwargs.update(image=icons['lock_icon.png'], compound='left')
send_button = tk.Button(window, **send_kwargs)
send_button.pack(pady=(0,10))

# Export buttons frame and buttons
export_frame = tk.Frame(window, bg=BG_COLOR)
export_frame.pack(pady=(0,20))
for label_text, cmd in [("Export as TXT", export_txt), ("Export as PDF", export_pdf)]:
    btn = tk.Button(export_frame, text=label_text, font=FONT_LABEL,
                    bg=BUTTON_BG, fg=BUTTON_FG,
                    relief='flat', bd=0, command=cmd)
    btn.pack(side='left', padx=10)

# Output area: scrollable, read-only until writing
output_area = scrolledtext.ScrolledText(window, wrap=tk.WORD,
    font=FONT_TEXT, bg=TEXT_BG, fg=TEXT_FG,
    insertbackground=TEXT_FG, relief='flat', bd=0)
output_area.pack(fill='both', expand=True, padx=20, pady=(0,20))
output_area.config(state='disabled')

# --------------------------------------------------
# 10) START THE GUI EVENT LOOP
# --------------------------------------------------
window.mainloop()
