from Docs2KG.modules.llm.markdown2json import LLMMarkdown2Json
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_md_file = DATA_OUTPUT_DIR / "4.pdf" / "text" / "md.csv"

    markdown2json = LLMMarkdown2Json(input_md_file)
    markdown2json.extract2json()
