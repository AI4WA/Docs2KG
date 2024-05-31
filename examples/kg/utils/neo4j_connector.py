from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    """
    This is to demonstrate how to load the triplets into Neo4j.

    After we have the output from the json2triplets.py,
    we can load the triplets into Neo4j.

    If you have a hosted Neo4j instance,
    you can change the uri to the hosted uri, also the username and password.

    If you do not, and just want to test out.

    All you need to do is get the docker installed
    Then run
    `docker compose -f examples/compose/docker-compose.yml up`
    """
    uri = "bolt://localhost:7687"  # if it is a remote graph db, you can change it to the remote uri
    username = "neo4j"
    password = "testpassword"
    json_file_path = DATA_OUTPUT_DIR / "4.pdf" / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
    neo4j_loader.load_data()
    neo4j_loader.close()
