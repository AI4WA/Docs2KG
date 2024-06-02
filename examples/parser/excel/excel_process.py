from Docs2KG.parser.excel.excel2image import Excel2Image
from Docs2KG.parser.excel.excel2markdown import Excel2Markdown
from Docs2KG.parser.excel.excel2table import Excel2Table
from Docs2KG.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    excel_file = DATA_INPUT_DIR / "excel" / "GCP_10002.xlsx"
    excel2table = Excel2Table(excel_file=excel_file)
    excel2table.extract_tables_from_excel()
    excel2image = Excel2Image(excel_file=excel_file)
    excel2image.excel2image_and_pdf()
    excel2markdown = Excel2Markdown(excel_file=excel_file)
    excel2markdown.extract2markdown()
