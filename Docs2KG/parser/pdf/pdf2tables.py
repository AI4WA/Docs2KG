from Docs2KG.utils.get_logger import get_logger
from Docs2KG.parser.pdf.base import PDFParserBase
import fitz

logger = get_logger(__name__)


class PDF2Tables(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the class with the pdf file
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables"
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2tables(self):
        """
        Extract images from the pdf file
        :return:
        """
        doc = fitz.open(self.pdf_file)  # open a document

        for page_index in range(len(doc)):  # iterate over pdf pages
            page = doc[page_index]  # get the page
            tabs = page.find_tables()
            if tabs.tables:
                logger.info(f"Found {len(tabs.tables)} tables on page {page_index}")
                for table_index, tab in enumerate(tabs.tables, start=1):
                    # save to csv
                    filename = "page_%s-table_%s.csv" % (page_index, table_index)
                    # save it to bounding box cropped image
                    df = tab.to_pandas()
                    df.to_csv(self.table_output_dir / filename)
