# aiGuiUbuntu.py
"""
Main GUI for CyberSafe AI Safety Hub
Leverages a custom LLM for Q&A and data analysis.
"""

import tkinter as tk
from tkinter import scrolledtext

# ==========
# CONFIG & DEPENDENCY IMPORTS
# ==========
from config import (
    BG_COLOR, FG_COLOR, HEADER_BG,
    BUTTON_BG, BUTTON_FG,
    ENTRY_BG, ENTRY_FG,
    TEXT_BG, TEXT_FG,
    FONT_HEADER, FONT_LABEL, FONT_ENTRY, FONT_TEXT,
    ICON_FILENAMES, WINDOW_TITLE,
)
import ai_functions.llm_client as llm_client
from ai_manager import call_ai_function, AVAILABLE_MODES
from utils.io_helpers import export_txt_widget, export_pdf_widget

# Initialize your LLM client once
llm_client.configure()

# ==========
# WINDOW SETUP
# ==========
window = tk.Tk()
window.title(WINDOW_TITLE)
window.configure(bg=BG_COLOR)

# Maximize window
import platform
if platform.system() == "Windows":
    window.state("zoomed")
else:
    try:
        window.attributes("-zoomed", True)
    except tk.TclError:
        window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")

# ==========
# LOAD ICONS
# ==========
icons = {}
for key, path in ICON_FILENAMES.items():
    if path.exists():
        icons[key] = tk.PhotoImage(file=str(path))

# Set window icon if available
if "noActionicon" in icons:
    window.iconphoto(True, icons["noActionicon"])

# ==========
# HEADER BAR
# ==========
hdr = tk.Frame(window, bg=HEADER_BG, pady=15)
hdr.pack(fill="x")
hdr_kwargs = {
    "text": WINDOW_TITLE,
    "font": FONT_HEADER,
    "bg": HEADER_BG,
    "fg": FG_COLOR
}
if "noActionicon" in icons:
    hdr_kwargs.update(image=icons["noActionicon"], compound="left")

tk.Label(hdr, **hdr_kwargs).pack()

# ==========
# MODE SELECTOR
# ==========
mode_label = tk.Label(window, text="AI Mode:", font=FONT_LABEL, bg=BG_COLOR, fg=FG_COLOR)
mode_label.pack(pady=(10, 5))
mode_var = tk.StringVar(value="Q&A")
mode_menu = tk.OptionMenu(window, mode_var, *AVAILABLE_MODES.keys())
mode_menu.config(font=FONT_LABEL, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", bd=0)
mode_menu.pack(pady=(0, 10))

# ==========
# PROMPT ENTRY FIELD
# ==========
tk.Label(window, text="Enter AI Prompt:", font=FONT_LABEL, bg=BG_COLOR, fg=FG_COLOR)\
    .pack(anchor="w", padx=20)
question_entry = tk.Entry(
    window,
    font=FONT_ENTRY,
    bg=ENTRY_BG,
    fg=ENTRY_FG,
    insertbackground=ENTRY_FG,
    relief="flat",
    bd=0
)
question_entry.pack(fill="x", padx=20, pady=(0, 10))
question_entry.focus()

# ==========
# SEND BUTTON CALLBACK
# ==========
def on_send() -> None:
    # Retrieve and validate prompt
    user_prompt = question_entry.get().strip()
    if not user_prompt:
        return

    # Clear output and show placeholder
    output_area.config(state="normal")
    output_area.delete("1.0", tk.END)

    # Show LLM icon if available
    if "llmicon" in icons:
        output_area.image_create(tk.END, image=icons["llmicon"])
        output_area.insert(tk.END, " ")

    placeholder_text = f"{mode_var.get()} AI Prompt:\n{user_prompt}\n\n"
    output_area.insert(tk.END, placeholder_text)

    # Show thinking icon or emoji
    if "clockicon" in icons:
        output_area.image_create(tk.END, image=icons["clockicon"])
        output_area.insert(tk.END, " Thinking…")
    else:
        output_area.insert(tk.END, "⏳ Thinking…")

    output_area.config(state="disabled")
    window.update_idletasks()

    # Call the AI and handle errors
    is_error = False
    try:
        answer = call_ai_function(mode_var.get(), user_prompt)
    except Exception:
        is_error = True
        answer = ""  # icon will indicate error

    # Display result or error icon
    output_area.config(state="normal")
    output_area.delete("1.0", tk.END)
    if is_error and "noActionicon" in icons:
        output_area.image_create(tk.END, image=icons["noActionicon"])
        output_area.insert(tk.END, " ")
        output_area.insert(tk.END, answer)
    else:
        output_area.insert(tk.END, answer)
    output_area.config(state="disabled")

# ==========
# SEND BUTTON
# ==========
send_kwargs = {
    "text": "Send AI Request ▶",
    "font": FONT_LABEL,
    "bg": BUTTON_BG,
    "fg": BUTTON_FG,
    "relief": "flat",
    "bd": 0,
    "command": on_send
}
if "clockicon" in icons:
    send_kwargs.update(image=icons["clockicon"], compound="left")
elif "noActionicon" in icons:
    send_kwargs.update(image=icons["noActionicon"], compound="left")

tk.Button(window, **send_kwargs).pack(pady=(0, 10))

# ==========
# EXPORT BUTTONS
# ==========
exp_frame = tk.Frame(window, bg=BG_COLOR)
exp_frame.pack(pady=(0, 20))

tk.Button(
    exp_frame,
    text="Export as TXT",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    relief="flat",
    bd=0,
    command=lambda: export_txt_widget(output_area)
).pack(side="left", padx=10)

tk.Button(
    exp_frame,
    text="Export as PDF",
    font=FONT_LABEL,
    bg=BUTTON_BG,
    fg=BUTTON_FG,
    relief="flat",
    bd=0,
    command=lambda: export_pdf_widget(output_area)
).pack(side="left", padx=10)

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
    relief="flat",
    bd=0
)
output_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
output_area.config(state="disabled")

# ==========
# MAIN LOOP
# ==========
window.mainloop()
