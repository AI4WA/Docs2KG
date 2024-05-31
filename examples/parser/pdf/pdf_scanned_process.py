from Docs2KG.modules.llm.markdown2json import LLMMarkdown2Json
from Docs2KG.parser.pdf.pdf2blocks import PDF2Blocks
from Docs2KG.parser.pdf.pdf2metadata import PDF_TYPE_SCANNED, get_scanned_or_exported
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pdf_file = DATA_INPUT_DIR / "3.pdf"
    output_folder = DATA_OUTPUT_DIR / "3.pdf"
    scanned_or_exported = get_scanned_or_exported(pdf_file)
    if scanned_or_exported == PDF_TYPE_SCANNED:
        logger.info(
            "This is a scanned pdf, we can only process it to the markdown and a image for whole page"
        )
        pdf_2_blocks = PDF2Blocks(pdf_file)
        blocks_dict = pdf_2_blocks.extract_df(output_csv=True)
        logger.info(blocks_dict)
        pdf_to_text = PDF2Text(pdf_file)
        text = pdf_to_text.extract2text(output_csv=True)
        md_text = pdf_to_text.extract2markdown(output_csv=True)
        ll_markdown2json = LLMMarkdown2Json(
            md_text["output_file"],
            llm_model_name="gpt-3.5-turbo",
        )
        logger.info("Cleaning the markdown file")
        ll_markdown2json.clean_markdown()
