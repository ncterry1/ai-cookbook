
# gui/Dockerfile (FILE)

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt   # openai, reportlab, neo4j-driver
COPY ai_chat_gui.py .               # Copy the GUI script
CMD ["python", "ai_chat_gui.py"]  # Launch the Tkinter GUI