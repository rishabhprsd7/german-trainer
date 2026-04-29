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
    MATCH (v:Word)
    WHERE toLower(v.name) = toLower($word)

    RETURN {
        word: v.name,
        meaning: coalesce(v.meaning, ""),
        type: coalesce(v.type, ""),
        example: coalesce(v.example, ""),
        perfect: coalesce(v.perfect, ""),
        reflexive: coalesce(v.reflexive, ""),
        level: coalesce(v.level, ""),
        set: coalesce(v.set, "")
    } AS data
    """

    result = run_query(query, {"word": word})

    if result:
        return result[0]["data"]

    return None
