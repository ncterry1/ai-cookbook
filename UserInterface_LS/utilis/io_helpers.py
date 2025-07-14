### HS_io_helpers.py (unchanged)
# I/O helper widgets for exporting chat content

def export_txt_widget(text: str, default_filename: str = "chat.txt"):
    # Prompt user for save location and write text file
    from tkinter import filedialog
    path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_filename)
    if path:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)


def export_pdf_widget(text: str, default_filename: str = "chat.pdf"):
    # Prompt user for save location and write simple PDF
    from tkinter import filedialog
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_filename)
    if path:
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        text_object = c.beginText(40, height - 40)
        for line in text.splitlines():
            text_object.textLine(line)
        c.drawText(text_object)
        c.save()