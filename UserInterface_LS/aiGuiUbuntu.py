### HS_aiGuiUbuntu.py
```python
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from HS_llm_client import ask
from HS_io_helpers import export_txt_widget, export_pdf_widget

class ChatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenAI Chat GUI")
        self.geometry("800x600")

        # Chat display
        self.chat_display = ScrolledText(self, state='disabled', wrap='word')
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=10)

        # User input
        input_frame = tk.Frame(self)
        input_frame.pack(fill='x', padx=10, pady=(0,10))
        self.user_input = tk.Entry(input_frame)
        self.user_input.pack(side='left', fill='x', expand=True)
        self.user_input.bind('<Return>', self.send_message)

        send_btn = tk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side='right')

        # Export buttons
        export_frame = tk.Frame(self)
        export_frame.pack(fill='x', padx=10)
        tk.Button(export_frame, text="Export TXT", command=lambda: export_txt_widget(self.chat_content())).pack(side='left')
        tk.Button(export_frame, text="Export PDF", command=lambda: export_pdf_widget(self.chat_content())).pack(side='left')

    def chat_content(self) -> str:
        return self.chat_display.get('1.0', 'end').strip()

    def append_message(self, role: str, msg: str):
        self.chat_display.configure(state='normal')
        self.chat_display.insert('end', f"{role}: {msg}\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see('end')

    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self.append_message("User", user_text)
        self.user_input.delete(0, 'end')

        try:
            response = ask(user_text)
        except Exception as e:
            response = f"Error: {e}"

        self.append_message("Assistant", response)

if __name__ == '__main__':
    app = ChatGUI()
    app.mainloop()