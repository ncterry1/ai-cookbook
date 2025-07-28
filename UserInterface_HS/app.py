from fastapi import FastAPI
from pydantic import BaseModel
from ai_functions.llm_client import ask, configure
from config import LLM_MODELS, LLM_DEFAULT_MODEL
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

# Lifespan context ensures configure() runs before handling requests
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and configure the LLM client
    configure()
    yield
    # (Optional) cleanup logic could go here on shutdown

# Create FastAPI app with custom lifespan
app = FastAPI(lifespan=lifespan)

# Pydantic model for /api/ask request validation
class AskRequest(BaseModel):
    prompt: str
    model: str | None = None


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

'''
We are using FastAPI
We do not want to expose our helper function llm_client.ask to the browser
Wrapping it in the 'endpoint' function to handle http plumbing (request parsing, response formatting, error handling etc.)
* @app.post("/api/ask") = a decorator
* @app.post - tells FastAPI that the function immediately below thi sdecorator should handle HTTP post requests
* ("/api/ask") - this string is the URL path that the function will handle. In this case, whenver the server receives a POST request to the associated page, FastAPI will call the decorated function.
---
app is our FastAPIT instance created with app=FastAPI()
.post() is the method on that instance which registers a handler for POST requests
The arguement "/api/ask" is the path at which this handler is mounted. 
'''
# LLM query endpoint
@app.post("/api/ask")
async def ask_model(request: AskRequest):
    # Ensure selected model is in the allowed list, otherwise use default
    model = request.model if request.model in LLM_MODELS else LLM_DEFAULT_MODEL
    try:
        # Call our llm_client.ask() helper
        response_text = ask(request.prompt, model=model)
        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

# Serve frontend static files
app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="static"
)
