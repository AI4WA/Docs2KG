"""
Input of the PDF will mainly from two sources:
- Scanned PDF
- Exported PDF

If it is a scanned PDF, we cannot process it into images and figures for now.
If it is an exported PDF, we can process it.

The function check_pdf_type will check the type of the PDF file.

"""

import Docs2KG.parser.pdf.base
import Docs2KG.parser.pdf.pdf2images
import Docs2KG.parser.pdf.pdf2tables
import Docs2KG.parser.pdf.pdf2text
import Docs2KG.parser.pdf.pdf_type
