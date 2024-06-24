import argparse

from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.kg.web_layout_kg import WebLayoutKG

if __name__ == "__main__":
    """
    Extract the HTML file to images, markdown, tables, and urls and save it to the output directory

    1. Get html, images, markdown, tables, and urls from the given URL
    """

    args = argparse.ArgumentParser()
    args.add_argument("--url", type=str, default=None, help="The URL")
    args.add_argument("--neo4j_uri", type=str, default="bolt://localhost:7687")
    args.add_argument("--neo4j_username", type=str, default="neo4j")
    args.add_argument("--neo4j_password", type=str, default="testpassword")

    if not args.url:
        url = "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA57080"

    web_layout_kg = WebLayoutKG(url=args.url)
    web_layout_kg.create_kg()

    semantic_kg = SemanticKG(
        folder_path=web_layout_kg.output_dir, input_format="html", llm_enabled=True
    )
    semantic_kg.add_semantic_kg()

    json_2_triplets = JSON2Triplets(web_layout_kg.output_dir)
    json_2_triplets.transform()

    json_file_path = web_layout_kg.output_dir / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(
        uri=args.neo4j_uri,
        username=args.neo4j_username,
        password=args.neo4j_password,
        json_file_path=json_file_path,
        clean=True,
    )
    neo4j_loader.load_data()
    neo4j_loader.close()
