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
    excel_file = DATA_INPUT_DIR / "excel" / "GCP_10002.xlsx"
    excel2table = Excel2Table(excel_file=excel_file)
    excel2table.extract_tables_from_excel()

    excel2image = Excel2Image(excel_file=excel_file)
    excel2image.excel2image_and_pdf()

    excel2markdown = Excel2Markdown(excel_file=excel_file)
    excel2markdown.extract2markdown()

    sheet_2_metadata = Sheet2Metadata(
        excel2markdown.md_csv,
        llm_model_name="gpt-3.5-turbo",
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
    uri = "bolt://localhost:7687"  # if it is a remote graph db, you can change it to the remote uri
    username = "neo4j"
    password = "testpassword"
    json_file_path = excel2markdown.output_dir / "kg" / "triplets_kg.json"

    neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
    neo4j_loader.load_data()
    neo4j_loader.close()
