from fastapi import FastAPI
from pydantic import BaseModel
from ai_functions.llm_client import ask

app = FastAPI()

# Request model for prompt submission
class AskRequest(BaseModel):
    prompt: str

@app.get("/api/health")
async def health_check():
    """Simple GET to verify the API is alive."""
    return {"status": "ok"}

@app.post("/api/ask")
async def api_ask(request: AskRequest):
    """Forwards the prompt to the LLM and returns its response."""
    response_text = ask(request.prompt)
    return {"response": response_text}

# Serve static files (the frontend) at the root path
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
