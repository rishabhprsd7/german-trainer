from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "german-db"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_word_details(word):
    with driver.session() as session:
        result = session.run("""
            MATCH (w:Word {name: $word})
            OPTIONAL MATCH (w)-[:PERFECT]->(p)
            OPTIONAL MATCH (w)-[:REFLEXIVE]->(r)
            RETURN 
                w.name AS word,
                w.meaning AS meaning,
                w.example AS example,
                w.type AS type,
                p.name AS perfect,
                r.name AS reflexive
        """, word=word)

        record = result.single()

        if record:
            return {
                "word": record["word"],
                "meaning": record["meaning"],
                "example": record["example"],
                "type": record["type"],
                "perfect": record["perfect"],
                "reflexive": record["reflexive"]
            }

        return None