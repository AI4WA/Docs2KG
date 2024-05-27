from Docs2KG.modules.native.markdown2json import Markdown2JSON
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_md_file = DATA_OUTPUT_DIR / "4.pdf" / "4.md"
    output_json_file = DATA_OUTPUT_DIR / "4.pdf" / "4.json"
    markdown2json = Markdown2JSON(input_md_file)
    markdown2json.extract2json()
