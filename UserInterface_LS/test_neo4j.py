from neo4j import GraphDatabase

# Connection settings
URI  = "bolt://localhost:7687"
AUTH = ("neo4j", "Pick6er@l22456N")

def create_and_read(tx):
    tx.run("MERGE (p:Person {name: $name})", name="Alice")
    result = tx.run("MATCH (p:Person) RETURN p.name AS name")
    return [record["name"] for record in result]

if __name__ == '__main__':
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # Use the modern API `execute_write()` for write operations (MERGE)
        names = session.execute_write(create_and_read)
        print("People in graph:", names)
    driver.close()