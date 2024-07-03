import argparse
from pathlib import Path

from Docs2KG.kg.excel_layout_kg import ExcelLayoutKG
from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.modules.llm.sheet2metadata import Sheet2Metadata
from Docs2KG.parser.excel.excel2image import Excel2Image
from Docs2KG.parser.excel.excel2markdown import Excel2Markdown
from Docs2KG.parser.excel.excel2table import Excel2Table
from Docs2KG.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    """
    Plan of the attack:

    1. For each sheet, extract the description stuff, and tables will be kept still in csv
    2. Then create the kg mainly based on the description
    """
    argparse = argparse.ArgumentParser()
    argparse.add_argument(
        "--excel_file", type=str, default=None, help="The Excel File Absolute Path"
    )
    argparse.add_argument(
        "--model_name", type=str, default="gpt-3.5-turbo", help="The model name"
    )
    argparse.add_argument("--neo4j_uri", type=str, default="bolt://localhost:7687")
    argparse.add_argument("--neo4j_username", type=str, default="neo4j")
    argparse.add_argument("--neo4j_password", type=str, default="testpassword")

    args = argparse.parse_args()
    # if you want to run this script, you can run it with `python excel.py --excel_file <excel_file>`
    if not args.excel_file:
        excel_file = DATA_INPUT_DIR / "excel" / "GCP_10002.xlsx"
    else:
        excel_file = Path(args.excel_file)

    excel2table = Excel2Table(excel_file=excel_file)
    excel2table.extract_tables_from_excel()

    excel2image = Excel2Image(excel_file=excel_file)
    excel2image.excel2image_and_pdf()

    excel2markdown = Excel2Markdown(excel_file=excel_file)
    excel2markdown.extract2markdown()

    sheet_2_metadata = Sheet2Metadata(
        excel2markdown.md_csv,
        llm_model_name=args.model_name,
    )
    sheet_2_metadata.extract_metadata()

    excel_layout_kg = ExcelLayoutKG(excel2markdown.output_dir, input_format="excel")
    excel_layout_kg.create_kg()
    # After this, you will have the layout.json in the `kg` folder

    # then we add the semantic knowledge graph
    semantic_kg = SemanticKG(
        excel2markdown.output_dir, llm_enabled=True, input_format="excel"
    )
    semantic_kg.add_semantic_kg()

    json_2_triplets = JSON2Triplets(excel2markdown.output_dir)
    json_2_triplets.transform()

    json_file_path = excel2markdown.output_dir / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(
        uri=args.neo4j_uri,
        username=args.neo4j_username,
        password=args.neo4j_password,
        json_file_path=json_file_path,
        clean=True,
    )
    neo4j_loader.load_data()
    neo4j_loader.close()
