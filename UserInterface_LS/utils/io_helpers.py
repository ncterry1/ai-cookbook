# utils/io_helpers.py
"""
Helper module for exporting the contents of a Tkinter Text widget to files.

This module provides two main functions:
  • export_txt_widget(widget):  Opens a file dialog and writes the widget’s text to a .txt file.
  • export_pdf_widget(widget):  Opens a file dialog and writes the widget’s text to a paginated, word-wrapped PDF.

Interactions:
  - Imported by aiGuiUbuntu.py: the main GUI script calls these functions via button callbacks,
    passing its output_area widget to save content.
  - Relies on config.py for PDF formatting settings (page size, margins, font, spacing).
  - Uses reportlab to generate PDFs and tkinter.filedialog to ask the user where to save.

No global state: each function accepts the widget to export, ensuring reusability across the app.
"""

import textwrap
from pathlib import Path
from tkinter import filedialog
from reportlab.pdfgen import canvas
from config import (
    PDF_PAGE_WIDTH,
    PDF_PAGE_HEIGHT,
    PDF_MARGIN_INCH,
    PDF_FONT,
    PDF_FONT_SIZE,
    PDF_LINE_SPACING, OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_DEFAULT_MODEL, BG_COLOR, FG_COLOR, HEADER_BG, BUTTON_BG, BUTTON_FG, ENTRY_BG, ENTRY_FG, TEXT_BG, TEXT_FG, FONT_ENTRY, FONT_TEXT, FONT_HEADER, FONT_LABEL, BASE_DIR, IMAGES_DIR, ICON_FILENAMES, WINDOW_TITLE, DEFAULT_VENV
)


def export_txt_widget(widget):
    """Save the contents of a Tkinter Text widget to a .txt file."""
    text = widget.get("1.0", "end")
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if path:
        Path(path).write_text(text, encoding="utf-8")


def export_pdf_widget(widget):
    """Save the contents of a Tkinter Text widget to a wrapped, paginated PDF."""
    text = widget.get("1.0", "end")
    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    if not path:
        return

    # Compute printable area in points (1 inch = 72 points)
    left_margin   = bottom_margin = PDF_MARGIN_INCH * 72
    page_width    = PDF_PAGE_WIDTH
    page_height   = PDF_PAGE_HEIGHT
    usable_width  = page_width - 2 * left_margin

    # Initialize PDF canvas
    pdf = canvas.Canvas(path, pagesize=(page_width, page_height))
    text_obj = pdf.beginText(left_margin, page_height - bottom_margin)
    text_obj.setFont(PDF_FONT, PDF_FONT_SIZE)
    text_obj.setLeading(PDF_FONT_SIZE * PDF_LINE_SPACING)

    # Determine wrap width in characters
    char_width = pdf.stringWidth('M', PDF_FONT, PDF_FONT_SIZE)
    wrap_width = max(1, int(usable_width / char_width))

    # Write lines with wrapping and pagination
    for line in text.splitlines():
        for segment in textwrap.wrap(line, width=wrap_width) or ['']:
            if text_obj.getY() <= bottom_margin:
                pdf.drawText(text_obj)
                pdf.showPage()
                text_obj = pdf.beginText(left_margin, page_height - bottom_margin)
                text_obj.setFont(PDF_FONT, PDF_FONT_SIZE)
                text_obj.setLeading(PDF_FONT_SIZE * PDF_LINE_SPACING)
            text_obj.textLine(segment)

    pdf.drawText(text_obj)
    pdf.save()
