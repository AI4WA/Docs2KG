from Docs2KG.kg.pdf_layout_kg import PDFLayoutKG
from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader
from Docs2KG.modules.llm.markdown2json import LLMMarkdown2Json
from Docs2KG.parser.pdf.pdf2blocks import PDF2Blocks
from Docs2KG.parser.pdf.pdf2image import PDF2Image
from Docs2KG.parser.pdf.pdf2metadata import PDF_TYPE_SCANNED, get_scanned_or_exported
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    """
    Here what we want to achieve is how to get the scanned PDF into the triplets for the Neo4j.

    We will require some of the OpenAI functions, we are currently default the model to `gpt-3.5-turbo`

    The cost itself is quite low, but you can determine whether you want to use it or not.

    Different from the exported PDF, current state of art still face some challenges in the scanned PDF
    Especially when trying to extract the figures and tables from the scanned PDF

    So we skip that step, only extract the text, and construct a layout knowledge graph based on the text
    Next is add the

    1. Extract Text, Images, Tables from the PDF
        - Extract text **block** and image **blocks** from the PDF
            - This will provide bounding boxes for the text and images
        - Extract tables from the PDF
        - Extract the text and markdown from the PDF, each page will be one markdown file
            - Output will be in a csv
    2. Markdown to JSON to get the foundation of the layout knowledge graph
        - There are two ways we can do this
        - However, the LLM based looks like much better than the rule based, due to the noise in the PDF
    3. Graph Construction, hook the page image to the layout knowledge graph
    """

    # you can name your file here
    pdf_file = DATA_INPUT_DIR / "3.pdf"

    output_folder = DATA_OUTPUT_DIR / "3.pdf"
    # the output will be default to `DATA_OUTPUT_DIR / "4.pdf" /` folder
    scanned_or_exported = get_scanned_or_exported(pdf_file)
    if scanned_or_exported == PDF_TYPE_SCANNED:
        logger.info("This is a scanned pdf, we will handle it in another demo")

        # This will extract the text, images.
        #
        # Output images/text with bounding boxes into a df
        pdf_2_blocks = PDF2Blocks(pdf_file)
        blocks_dict = pdf_2_blocks.extract_df(output_csv=True)
        logger.info(blocks_dict)

        # Processing the text from the pdf file
        # For each page, we will have a markdown and text content,
        # Output will be in a csv

        pdf_to_text = PDF2Text(pdf_file)
        text = pdf_to_text.extract2text(output_csv=True)
        md_text = pdf_to_text.extract2markdown(output_csv=True)

        # Until now, your output folder should be some like this
        # .
        # ├── 4.pdf
        # ├── images
        # │         ├── blocks_images.csv
        # │         ├── page_0_block_1.jpeg
        # │         ├── page_0_block_4.jpeg
        # │         ├── ....
        # ├── metadata.json
        # └── texts
        #     ├── blocks_texts.csv
        #     ├── md.csv
        #     └── text.csv
        # under the image folder, are not valid image, we need better models for that.
        input_md_file = output_folder / "texts" / "md.csv"

        markdown2json = LLMMarkdown2Json(
            input_md_file,
            llm_model_name="gpt-3.5-turbo",
        )

        markdown2json.clean_markdown()
        markdown2json.markdown_file = output_folder / "texts" / "md.cleaned.csv"

        markdown2json.extract2json()

        pdf_2_image = PDF2Image(pdf_file)
        pdf_2_image.extract_page_2_image_df()
        # after this we will have a added `md.json.csv` in the `texts` folder

        # next we will start to extract the layout knowledge graph first

        layout_kg = PDFLayoutKG(output_folder, scanned_pdf=True)
        layout_kg.create_kg()

        # After this, you will have the layout.json in the `kg` folder

        # then we add the semantic knowledge graph
        semantic_kg = SemanticKG(
            output_folder, llm_enabled=True, input_format="pdf_scanned"
        )
        semantic_kg.add_semantic_kg()

        # After this, the layout_kg.json will be augmented with the semantic connections
        # in the `kg` folder

        # then we do the triplets extraction
        json_2_triplets = JSON2Triplets(output_folder)
        json_2_triplets.transform()

        # After this, you will have the triplets_kg.json in the `kg` folder
        # You can take it from here, load it into your graph db, or handle it in any way you want

        # If you want to load it into Neo4j, you can refer to the `examples/kg/utils/neo4j_connector.py`
        # to get it quickly loaded into Neo4j
        # You can do is run the `docker compose -f examples/compose/docker-compose.yml up`
        # So we will have a Neo4j instance running, then you can run the `neo4j_connector.py` to load the data
        uri = "bolt://localhost:7687"  # if it is a remote graph db, you can change it to the remote uri
        username = "neo4j"
        password = "testpassword"
        json_file_path = output_folder / "kg" / "triplets_kg.json"

        neo4j_loader = Neo4jLoader(uri, username, password, json_file_path, clean=True)
        neo4j_loader.load_data()
        neo4j_loader.close()
    else:
        logger.info("This is an exported pdf, we will handle it in another demo")
