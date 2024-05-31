from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "testpassword"
    json_file_path = DATA_OUTPUT_DIR / "4.pdf" / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
    neo4j_loader.load_data()
    neo4j_loader.close()
