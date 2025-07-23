# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from neo4j import GraphDatabase
# Need these 3 below to move back one directory to import associated modules
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_functions.llm_client import ask

class AskRequest(BaseModel):
    prompt: str

app = FastAPI()
# Neo4j driver setup (Bolt)
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "Pick6er@l22456N")
)

@app.get("/api/health")
async def health_check():
    # Basic liveness check
    return {"status": "ok"}

@app.post("/api/ask")
async def api_ask(request: AskRequest):
    # Accepts JSON {"prompt": str} and returns LLM response
    # Calls the ask() function in ai_functions/llm_client.py
    response = ask(request.prompt)
    return {"response": response}

@app.post("/api/query-graph")
async def query_graph(q: str):
    # Executes a Cypher query against Neo4j and returns records
    with driver.session() as session:
        result = session.run(q)
        return {"records": [dict(r) for r in result]}

# Serve frontend static files
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")