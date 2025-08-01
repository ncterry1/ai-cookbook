import json
from pathlib import Path
from neo4j import GraphDatabase

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def ingest_email(tx, email):
    query = """
    MERGE (s:User {email: $sender})
    MERGE (r:User {email: $receiver})
    MERGE (s)-[e:SENT_EMAIL {subject: $subject, timestamp: datetime($timestamp)}]->(r)
    """
    tx.run(query, email)

if __name__ == '__main__':
    emails = json.loads((Path(__file__).parent / 'email_data.json').read_text())
    with driver.session() as session:
        for e in emails:
            session.execute_write(ingest_email, e)
    driver.close()
    print("Emails ingested successfully.")