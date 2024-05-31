from Docs2KG.modules.llm.markdown2json import LLMMarkdown2Json
from Docs2KG.parser.pdf.pdf2blocks import PDF2Blocks
from Docs2KG.parser.pdf.pdf2metadata import PDF_TYPE_SCANNED, get_scanned_or_exported
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    """
    Here what we want to achieve is how to get the exported PDF into the triplets for the Neo4j.

    We will require some of the OpenAI functions, we are currently default the model to `gpt-3.5-turbo`

    The cost itself is quite low, but you can determine whether you want to use it or not.

    Overall steps include:

    1. Extract Text, Images, Tables from the PDF
        - Extract text **block** and image **blocks** from the PDF
            - This will provide bounding boxes for the text and images
        - Extract tables from the PDF
        - Extract the text and markdown from the PDF, each page will be one markdown file
            - Output will be in a csv
    2. Markdown to JSON to get the foundation of the layout knowledge graph
        - There are two ways we can do this
        - However, the LLM based looks like much better than the rule based, due to the noise in the PDF
    3. Graph Construction
    """

    # you can name your file here
    pdf_file = DATA_INPUT_DIR / "tests_pdf" / "4.pdf"
    # the output will be default to `DATA_OUTPUT_DIR / "4.pdf" /` folder
    scanned_or_exported = get_scanned_or_exported(pdf_file)
    if scanned_or_exported == PDF_TYPE_SCANNED:
        logger.info("This is a scanned pdf, we will handle it in another demo")
    else:
        # This will extract the text, images.
        #
        # Output images/text with bounding boxes into a df
        pdf_2_blocks = PDF2Blocks(pdf_file)
        blocks_dict = pdf_2_blocks.extract_df(output_csv=True)
        logger.info(blocks_dict)

        # This will extract the tables from the pdf file
        # Output also will be the csv of the summary and each individual table csv

        pdf2tables = PDF2Tables(pdf_file)
        pdf2tables.extract2tables(output_csv=True)

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
        # ├── tables
        # │         ├── page_16-table_1.csv
        # │         ├── ....
        # │         └── tables.csv
        # └── texts
        #     ├── blocks_texts.csv
        #     ├── md.csv
        #     └── text.csv

        input_md_file = DATA_OUTPUT_DIR / "4.pdf" / "texts" / "md.csv"

        markdown2json = LLMMarkdown2Json(
            input_md_file,
            llm_model_name="gpt-3.5-turbo",
        )
        markdown2json.extract2json()

        # after this we will have a added `md.json.csv` in the `texts` folder
