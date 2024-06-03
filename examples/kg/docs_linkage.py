import json

from Docs2KG.kg.docs_linkage import DocsLinkage
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    input_folder = DATA_INPUT_DIR / "docslinkage" / "docs.json"

    docs_linkage = DocsLinkage(input_folder)
    rels = docs_linkage.openai_link_docs()
    uri = "bolt://localhost:7687"  # if it is a remote graph db, you can change it to the remote uri
    username = "neo4j"
    password = "testpassword"
    # get the rels into a temp file json
    json_file_path = DATA_INPUT_DIR / "docslinkage" / "docs_linkage.json"
    json_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_file_path, "w") as f:
        json.dump(rels, f)

    neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
    neo4j_loader.load_data()
    neo4j_loader.close()
    # remove the temp file
    json_file_path.unlink()
