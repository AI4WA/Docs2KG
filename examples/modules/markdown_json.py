from Docs2KG.modules.markdown2json import Markdown2JSON
from Docs2KG.parser.pdf.pdf2blocks import PDF2DataFrame
from Docs2KG.parser.pdf.pdf2images import PDF2Images
from Docs2KG.parser.pdf.pdf2metadata import PDF_TYPE_SCANNED, get_scanned_or_exported
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.utils.constants import DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

if __name__ == "__main__":
    input_md_file = DATA_OUTPUT_DIR / "4.pdf" / "4.md"
    output_json_file = DATA_OUTPUT_DIR / "4.pdf" / "4.json"
    markdown2json = Markdown2JSON(input_md_file)
    markdown2json.extract2json()
