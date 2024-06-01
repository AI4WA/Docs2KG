from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.kg.web_layout_kg import WebLayoutKG

if __name__ == "__main__":
    """
    Extract the HTML file to images, markdown, tables, and urls and save it to the output directory

    1. Get html, images, markdown, tables, and urls from the given URL
    """
    url = "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA57080"

    web_layout_kg = WebLayoutKG(url=url)
    web_layout_kg.create_kg()

    semantic_kg = SemanticKG(
        folder_path=web_layout_kg.output_dir, input_format="html", llm_enabled=True
    )
    semantic_kg.add_semantic_kg()

    json_2_triplets = JSON2Triplets(web_layout_kg.output_dir)
    json_2_triplets.transform()
    uri = "bolt://localhost:7687"  # if it is a remote graph db, you can change it to the remote uri
    username = "neo4j"
    password = "testpassword"
    json_file_path = web_layout_kg.output_dir / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
    neo4j_loader.load_data()
    neo4j_loader.close()
