"""
ai_chat_gui.py

A sleek, cybersecurity-themed maximized desktop GUI to ask questions of an OpenAI LLM.

-------------------------------------------------------------------------------
INSTALLATION NOTES:
  • Requires the OpenAI Python client >=1.0.0:
      pip install --upgrade openai
  • Tkinter is part of the Python standard library on most platforms.
    If you get an ImportError on tkinter:
      • Debian/Ubuntu: sudo apt install python3-tk
      • Fedora:        sudo dnf install python3-tkinter
      • Windows/macOS: normally included with your Python installer.
  • Set your API key in your environment before running:
      export OPENAI_API_KEY="your_api_key_here"   # macOS/Linux
      set OPENAI_API_KEY="your_api_key_here"      # Windows PowerShell
-------------------------------------------------------------------------------
"""

import os
import openai                      # OpenAI client library (v1.x interface)
import tkinter as tk               # Standard GUI toolkit
from tkinter import scrolledtext  # Text widget with built-in scrollbar

# -----------------------------------------------------------------------------
# Color & Font Theme (Nord-Inspired)
# -----------------------------------------------------------------------------
BG_COLOR     = "#2E3440"  # Dark background
FG_COLOR     = "#ECEFF4"  # Light text
HEADER_BG    = "#4C566A"  # Header background
BUTTON_BG    = "#5E81AC"  # Button background
BUTTON_FG    = "#ECEFF4"  # Button text
ENTRY_BG     = "#3B4252"  # Entry background
ENTRY_FG     = "#ECEFF4"  # Entry text
TEXT_BG      = "#3B4252"  # Text widget background
TEXT_FG      = "#D8DEE9"  # Text widget text
FONT_HEADER  = ("Consolas", 18, "bold")
FONT_LABEL   = ("Consolas", 14)
FONT_ENTRY   = ("Consolas", 14)
FONT_TEXT    = ("Consolas", 12)

# -----------------------------------------------------------------------------
# 1. Configure OpenAI API key
# -----------------------------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# -----------------------------------------------------------------------------
# 2. Define the function to send a question to the LLM and display the reply
# -----------------------------------------------------------------------------
def ask_openai():
    """
    1. Grab the question from the input field.
    2. Show 'Thinking…' placeholder.
    3. Use the new chat.completions.create interface.
    4. Display the assistant's response (or error).
    """
    question = question_entry.get().strip()
    if not question:
        return

    # Show placeholder
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, f"🔍 You asked:\n{question}\n\n⏳ Thinking…\n")
    output_area.config(state='disabled')
    window.update_idletasks()

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful cybersecurity assistant."},
                {"role": "user",   "content": question},
            ],
            temperature=0.5,
            max_tokens=512,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"❌ Error calling OpenAI API:\n{e}"

    # Display the answer
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, answer)
    output_area.config(state='disabled')

# -----------------------------------------------------------------------------
# 3. Build the Tkinter UI (maximized with standard controls)
# -----------------------------------------------------------------------------
window = tk.Tk()
window.title("🔒 Cybersecurity AI Chat")
window.state('zoomed')                # Maximize with title bar intact
window.configure(bg=BG_COLOR)         # Window background
window.bind("<Escape>", lambda e: window.state('normal'))  # Un-maximize

# Header Frame
header_frame = tk.Frame(window, bg=HEADER_BG, pady=15)
header_frame.pack(fill='x')
header_label = tk.Label(
    header_frame,
    text="🔒 Cybersecurity AI Chat Interface",
    font=FONT_HEADER,
    bg=HEADER_BG,
    fg=FG_COLOR
)
header_label.pack()

# Instruction Label
instruction_label = tk.Label(
    window,
    text="Enter your security question below:",
    font=FONT_LABEL,
    bg=BG_COLOR,
    fg=FG_COLOR
)
instruction_label.pack(pady=(10,5))

# Question Entry
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=FG_COLOR,  # Cursor color
    relief='flat',
    bd=5                       # Border width
)
question_entry.pack(fill='x', padx=20, pady=(0,15))
question_entry.focus()

# Send Button
send_button = tk.Button(
    window,
    text="Send ▶",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    activebackground=HEADER_BG,
    relief='raised',
    bd=3,
    command=ask_openai
)
send_button.pack(pady=(0,20))

# Output Text Area
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
output_area.config(state='disabled')

# -----------------------------------------------------------------------------
# 4. Start the Tkinter event loop
# -----------------------------------------------------------------------------
window.mainloop()
