from neo4j import GraphDatabase
import os

# Read from environment variables
URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def run_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]

def get_word_details(word):
    query = """
    MATCH (w:Word {name: $word})
    OPTIONAL MATCH (w)-[:PERFECT]->(p)
    OPTIONAL MATCH (w)-[:REFLEXIVE]->(r)
    RETURN w.name AS word,
           w.meaning AS meaning,
           w.example AS example,
           p.name AS perfect,
           r.name AS reflexive
    """

    result = run_query(query, {"word": word})

    if result:
        return result[0]

    return None
