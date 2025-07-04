"""
ai_chat_gui.py

A sleek, cybersecurity-themed maximized desktop GUI that supports multiple AI functions
from separate scripts in the `ai_functions` package.

-------------------------------------------------------------------------------
INSTALLATION NOTES:
  • Requires the OpenAI Python client >=1.0.0:
      pip install --upgrade openai
  • Tkinter is part of the Python standard library on most platforms.
    If you get an ImportError on tkinter:
      • Debian/Ubuntu: sudo apt install python3-tk
      • Fedora:        sudo dnf install python3-tkinter
      • Windows/macOS: normally included with your Python installer.
  • Ensure you have an `ai_functions` folder with at least `qa.py` and `data_analysis.py`:
      mkdir ai_functions
      # Then create ai_functions/qa.py and ai_functions/data_analysis.py based on stubs below
  • Set your API key in your environment before running:
      export OPENAI_API_KEY="your_api_key_here"   # macOS/Linux
      set OPENAI_API_KEY="your_api_key_here"      # Windows PowerShell
-------------------------------------------------------------------------------
"""

# Standard library imports
import os                  # Access environment variables
import importlib           # Dynamically import modules at runtime

# External library import
import openai              # OpenAI client library (>=1.0.0 interface)

# GUI library imports
import tkinter as tk                           # Core Tkinter functionality
from tkinter import scrolledtext               # ScrolledText widget for output area

# ----------------------------------------------------------------------------
# Color & Font Theme (Nord-Inspired)
# ----------------------------------------------------------------------------
BG_COLOR     = "#2E3440"  # Dark slate background
FG_COLOR     = "#ECEFF4"  # Off-white text
HEADER_BG    = "#4C566A"  # Muted gray-blue header
BUTTON_BG    = "#5E81AC"  # Steel blue buttons
BUTTON_FG    = "#ECEFF4"  # Off-white button text
ENTRY_BG     = "#3B4252"  # Dark gray entry background
ENTRY_FG     = "#ECEFF4"  # Off-white entry text
TEXT_BG      = "#3B4252"  # Dark gray text area background
TEXT_FG      = "#D8DEE9"  # Light gray text area text
FONT_HEADER  = ("Consolas", 18, "bold")  # Header font: Consolas 18 bold
FONT_LABEL   = ("Consolas", 14)            # Label font: Consolas 14
FONT_ENTRY   = ("Consolas", 14)            # Entry font: Consolas 14
FONT_TEXT    = ("Consolas", 12)            # Text area font: Consolas 12

# ----------------------------------------------------------------------------
# 1. Configure OpenAI API key
# ----------------------------------------------------------------------------
# Read API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
# Halt if key is missing
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# ----------------------------------------------------------------------------
# 2. Define available AI modes and dynamic loader
# ----------------------------------------------------------------------------
# Map user-friendly mode names to module paths under ai_functions/
# Note: These are Python module names (dot-separated), not file paths. When importing modules
#       with importlib.import_module, you omit the '.py' extension. For example,
#       importlib.import_module('ai_functions.qa') will load ai_functions/qa.py.
AVAILABLE_MODES = {
    "Q&A":           "ai_functions.qa",             # Basic question-answering mode (ai_functions/qa.py)
    "Data Analysis": "ai_functions.data_analysis",  # Data analysis mode (ai_functions/data_analysis.py)
    # To add more modes, reference the module name without '.py':
    # "Your Mode": "ai_functions.your_module"
}

# Example usage (outside GUI):
#   answer = call_ai_function("Q&A", "What is a buffer overflow?")
#   print(answer)

def call_ai_function(mode, prompt):
    """
    Dynamically import the module for `mode` and call its run() function.

    Args:
        mode (str): Key from AVAILABLE_MODES, e.g., "Q&A".
        prompt (str): User's input prompt.

    Returns:
        str: The response string returned by the module's run() function.

    Raises:
        ValueError: If mode not in AVAILABLE_MODES.
        AttributeError: If module lacks a run(prompt) function.

    Example:
        >>> call_ai_function("Data Analysis", "Sales data for Q2")
        'Analysis results...'
    """
    # Get module path
    module_name = AVAILABLE_MODES.get(mode)
    if module_name is None:
        raise ValueError(f"Unknown mode: {mode}")
    # Import module
    module = importlib.import_module(module_name)
    # Check for run()
    if not hasattr(module, "run"):
        raise AttributeError(f"Module '{module_name}' missing 'run(prompt)' function")
    # Call run()
    return module.run(prompt)

# ----------------------------------------------------------------------------
# 3. Build the Tkinter UI (maximized with decorations)
# ----------------------------------------------------------------------------
# Create main window
window = tk.Tk()
# Window title
window.title("🔒 Cybersecurity AI Chat")
# Maximize window (retains title bar controls)
window.state('zoomed')
# Set background color
window.configure(bg=BG_COLOR)
# Bind Esc to restore window
window.bind('<Escape>', lambda e: window.state('normal'))

# Header frame
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)
header_frame.pack(fill='x')  # Stretch horizontally
# Header label
tk.Label(
    header_frame,
    text="🔒 Cybersecurity AI Chat Interface",
    font=FONT_HEADER,
    bg=HEADER_BG,
    fg=FG_COLOR
).pack()

# Mode selection frame
mode_var = tk.StringVar(value="Q&A")  # Default mode
mode_frame = tk.Frame(window, bg=BG_COLOR)
mode_frame.pack(pady=(10,5))
# Mode label
tk.Label(
    mode_frame,
    text="Mode:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
).pack(side='left', padx=(20,5))
# Mode dropdown
mode_menu = tk.OptionMenu(mode_frame, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG)
mode_menu.pack(side='left')

# Prompt instruction label
tk.Label(
    window,
    text="Enter your prompt below:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
).pack(pady=(10,5))

# Prompt entry widget
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=FG_COLOR,
    relief='flat',
    bd=5
)
question_entry.pack(fill='x', padx=20, pady=(0,15))
question_entry.focus()  # Focus keyboard

# Send button
send_button = tk.Button(
    window,
    text="Send ▶",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    activebackground=HEADER_BG,
    relief='raised',
    bd=3,
    command=lambda: on_send()
)
send_button.pack(pady=(0,20))

# Output text area
output_area = scrolledtext.ScrolledText(
    window,
    wrap=tk.WORD,
    font=FONT_TEXT,
    bg=TEXT_BG,
    fg=TEXT_FG,
    insertbackground=FG_COLOR,
    relief='flat',
    bd=5
)
output_area.pack(fill='both', expand=True, padx=20, pady=(0,20))
output_area.config(state='disabled')  # Read-only

# ----------------------------------------------------------------------------
# 4. Handle Send action
# ----------------------------------------------------------------------------
def on_send():
    # Retrieve prompt and trim whitespace
    prompt = question_entry.get().strip()
    if not prompt:
        return  # Do nothing if empty

    # Show placeholder
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(
        tk.END,
        f"🔍 {mode_var.get()} Prompt:\n{prompt}\n\n⏳ Thinking…\n"
    )
    output_area.config(state='disabled')
    window.update_idletasks()  # Refresh UI

    try:
        # Call AI function based on mode
        response = call_ai_function(mode_var.get(), prompt)
    except Exception as e:
        response = f"❌ Error: {e}"

    # Display response
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, response)
    output_area.config(state='disabled')

# ----------------------------------------------------------------------------
# 5. Start GUI event loop
# ----------------------------------------------------------------------------
window.mainloop()