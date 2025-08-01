import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from ai_functions.llm_client import ask_llm
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
from neo4j import GraphDatabase

app = FastAPI()

# Mount frontend directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# Database connection setup
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class UserPrompt(BaseModel):
    prompt: str
    model: str | None = None

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/query_graph")
async def query_graph(request: UserPrompt):
    response = ask_llm(request.prompt, request.model)
    return {"llm_response": response}

@app.get("/api/get_graph")
async def get_graph():
    with driver.session() as session:
        results = session.run("MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 100")
        graph_data = [{
            "source": record["n"].id,
            "target": record["m"].id,
            "relationship": type(record["r"])
        } for record in results]
    return {"graph": graph_data}
