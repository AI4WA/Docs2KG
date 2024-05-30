from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_folder = DATA_OUTPUT_DIR / "4.pdf"

    layout_kg = SemanticKG(input_folder, llm_enabled=True)
    layout_kg.add_semantic_kg()
