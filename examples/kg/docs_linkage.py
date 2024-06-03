from Docs2KG.kg.docs_linkage import DocsLinkage
from Docs2KG.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    input_folder = DATA_INPUT_DIR / "docslinkage" / "docs.json"

    docs_linkage = DocsLinkage(input_folder)
    rels = docs_linkage.openai_link_docs()
    print(rels)
