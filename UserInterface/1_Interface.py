"""
ai_chat_gui.py

A simple desktop GUI (maximized with standard window controls) to ask questions of an OpenAI LLM.

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

    # Show placeholder text
    output_area.config(state='normal')
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.END, f"You asked:\n{question}\n\nThinking…\n")
    output_area.config(state='disabled')
    window.update_idletasks()  # Force UI refresh to show "Thinking…"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",    # or "gpt-4" if you have access
            messages=[
                {"role": "system",  "content": "You are a helpful assistant."},
                {"role": "user",    "content": question},
            ],
            temperature=0.7,
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
# 3. Build the Tkinter UI (maximized with decorations)
# -----------------------------------------------------------------------------
window = tk.Tk()
window.title("AI Chat Interface")

# Instead of true fullscreen (which removes the title bar), maximize the window.
# On Windows and many Linux setups, 'zoomed' opens with min/max/close buttons intact.
window.state('zoomed')

# Optional: bind Esc to restore to a normal window (un-maximize)
window.bind("<Escape>", lambda e: window.state('normal'))

# Instruction label
tk.Label(window, text="Enter your question below:",
         font=("Arial", 12)).pack(pady=(10, 0))

# Single-line Entry for the question
question_entry = tk.Entry(window, font=("Arial", 12))
question_entry.pack(fill='x', padx=20, pady=10)
question_entry.focus()

# Send button
send_button = tk.Button(window, text="Send ▶",
                        font=("Arial", 12, "bold"),
                        command=ask_openai)
send_button.pack(pady=(0,10))

# Scrolled text area for the AI's response
output_area = scrolledtext.ScrolledText(window, wrap=tk.WORD,
                                        font=("Arial", 12))
output_area.pack(fill='both', expand=True, padx=20, pady=(0,20))
output_area.config(state='disabled')

# -----------------------------------------------------------------------------
# 4. Start the Tkinter event loop
# -----------------------------------------------------------------------------
window.mainloop()
