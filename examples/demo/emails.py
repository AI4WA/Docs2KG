from Docs2KG.kg.email_layout_kg import EmailLayoutKG
from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.parser.email.email_compose import EmailDecompose
from Docs2KG.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    email_filename = DATA_INPUT_DIR / "email.eml"
    email_decomposer = EmailDecompose(email_file=email_filename)
    email_decomposer.decompose_email()

    email_layout_kg = EmailLayoutKG(output_dir=email_decomposer.output_dir)
    email_layout_kg.create_kg()

    semantic_kg = SemanticKG(
        email_decomposer.output_dir, llm_enabled=True, input_format="email"
    )
    semantic_kg.add_semantic_kg()

    json_2_triplets = JSON2Triplets(email_decomposer.output_dir)
    json_2_triplets.transform()
    uri = "bolt://localhost:7687"  # if it is a remote graph db, you can change it to the remote uri
    username = "neo4j"
    password = "testpassword"
    json_file_path = email_decomposer.output_dir / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
    neo4j_loader.load_data()
    neo4j_loader.close()
