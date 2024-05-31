from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.web_layout_kg import WebLayoutKG

if __name__ == "__main__":
    """
    Extract the HTML file to images, markdown, tables, and urls and save it to the output directory

    1. Get html, images, markdown, tables, and urls from the given URL
    """
    url = "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA57080"

    web_layout_kg = WebLayoutKG(url=url)
    web_layout_kg.create_kg()

    semantic_kg = SemanticKG(
        folder_path=web_layout_kg.output_dir, input_format="html", llm_enabled=True
    )
    semantic_kg.add_semantic_kg()
