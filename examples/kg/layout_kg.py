from Docs2KG.kg.layout_kg import LayoutKG
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_folder = DATA_OUTPUT_DIR / "4.pdf"

    layout_kg = LayoutKG(input_folder)
    layout_kg.create_kg()
