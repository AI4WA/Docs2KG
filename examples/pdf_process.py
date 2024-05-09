from BlackSwan.pdf_parser.pdf2text import PDF2Text
from BlackSwan.pdf_parser.pdf2images import PDF2Images
from BlackSwan.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    pdf_file = DATA_INPUT_DIR / "1.pdf"
    # pdf2text = PDF2Text(pdf_file)
    # text = pdf2text.extract2text()
    # md_text = pdf2text.extract2markdown()
    pdf2images = PDF2Images(pdf_file)
    pdf2images.extract2images()
