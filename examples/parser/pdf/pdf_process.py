from Docs2KG.parser.pdf.pdf2blocks import PDF2Blocks
from Docs2KG.parser.pdf.pdf2metadata import PDF_TYPE_SCANNED, get_scanned_or_exported
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.utils.constants import DATA_INPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pdf_file = DATA_INPUT_DIR / "OMR241-Chartbook.pdf"
    scanned_or_exported = get_scanned_or_exported(pdf_file)
    if scanned_or_exported == PDF_TYPE_SCANNED:
        logger.info("This is a scanned pdf, can not process it now")
    else:
        """
        This will extract the text, images.

        Output images/text with bounding boxes into a df

        """
        pdf_2_blocks = PDF2Blocks(pdf_file)
        blocks_dict = pdf_2_blocks.extract_df(output_csv=True)
        logger.info(blocks_dict)

        """
        This will extract the tables from the pdf file
        """
        pdf2tables = PDF2Tables(pdf_file)
        pdf2tables.extract2tables(output_csv=True)

        """
        Processing the text from the pdf file
        """

        pdf_to_text = PDF2Text(pdf_file)
        text = pdf_to_text.extract2text(output_csv=True)
        md_text = pdf_to_text.extract2markdown(output_csv=True)
