from Docs2KG.modules.llm.markdown2json import LLMMarkdown2Json
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    input_md_file = DATA_OUTPUT_DIR / "3.pdf" / "texts" / "md.csv"

    markdown2json = LLMMarkdown2Json(
        input_md_file,
        llm_model_name="gpt-3.5-turbo",
    )
    markdown2json.clean_markdown()
