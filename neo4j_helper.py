from neo4j import GraphDatabase
import os

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def run_query(query, parameters=None):
    with driver.session(database=DATABASE) as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def get_word_details(word):
    query = """
    MATCH (v:Vocabulary {word: $word})
    RETURN v.word AS word,
           v.meaning AS meaning,
           v.type AS type,
           v.example AS example,
           v.perfect AS perfect,
           v.reflexive AS reflexive
    """

    result = run_query(query, {"word": word})

    if result:
        return result[0]

    return None
