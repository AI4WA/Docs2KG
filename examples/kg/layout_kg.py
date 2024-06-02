from Docs2KG.kg.pdf_layout_kg import PDFLayoutKG
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_folder = DATA_OUTPUT_DIR / "4.pdf"

    layout_kg = PDFLayoutKG(input_folder)
    layout_kg.create_kg()
