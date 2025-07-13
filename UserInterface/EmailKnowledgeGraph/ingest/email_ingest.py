'''
ingest/email_ingest.py (FILE)

Python script to:
1) Read raw email files in emails/ directory.
2) Parse each into fields: id, date, sender, recipients, subject, body.
3) Connect to Neo4j via Bolt using neo4j-driver.
4) MERGE nodes and relationships:

--- (:Email {id}), properties for date, subject, body.

--- (:Person {email}) for sender and recipients.

--- (:Person)-[:SENT]->(:Email) and (:Email)-[:TO]->(:Person).

It reads connection details from environment variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) loaded via python-dotenv.
'''