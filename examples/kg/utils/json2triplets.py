from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_folder = DATA_OUTPUT_DIR / "4.pdf"

    layout_kg = JSON2Triplets(input_folder)
    layout_kg.transform()
