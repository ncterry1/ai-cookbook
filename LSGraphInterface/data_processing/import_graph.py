from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def import_data():
    with driver.session() as session:
        # Placeholder for future data import logic
        session.run("CREATE (n:Node {name: 'Example'})")

if __name__ == "__main__":
    import_data()
