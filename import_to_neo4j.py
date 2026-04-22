from neo4j import GraphDatabase
import json
import os

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "german-db"

DATA_FOLDER = "data"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def import_file(filepath, level, set_name):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    with driver.session() as session:
        for item in data:
            word = item["word"]
            meaning = item["meaning"]
            example = item["example"]
            wtype = item["type"]
            perfect = item.get("perfect")
            reflexive = item.get("reflexive")

            # WORD NODE
            session.run("""
                MERGE (w:Word {name: $word})
                SET w.meaning = $meaning,
                    w.example = $example,
                    w.type = $type,
                    w.level = $level,
                    w.set = $set
            """, word=word, meaning=meaning, example=example,
                 type=wtype, level=level, set=set_name)

            # PERFECT
            if perfect:
                session.run("""
                    MERGE (p:Form {name: $perfect})
                    WITH p
                    MATCH (w:Word {name: $word})
                    MERGE (w)-[:PERFECT]->(p)
                """, perfect=perfect, word=word)

            # REFLEXIVE
            if reflexive:
                session.run("""
                    MERGE (r:Form {name: $reflexive})
                    WITH r
                    MATCH (w:Word {name: $word})
                    MERGE (w)-[:REFLEXIVE]->(r)
                """, reflexive=reflexive, word=word)


def run_import():
    for file in os.listdir(DATA_FOLDER):

        if not file.endswith(".json"):
            continue

        parts = file.replace(".json", "").split("_")

        if len(parts) != 2:
            print(f"Skipping invalid file: {file}")
            continue

        level, set_name = parts

        path = os.path.join(DATA_FOLDER, file)

        print(f"📂 Importing {file}...")
        import_file(path, level, set_name)

    print("✅ Import complete!")


if __name__ == "__main__":
    run_import()