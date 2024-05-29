from Docs2KG.parser.excel.excel2table import Excel2Table

if __name__ == "__main__":
    excel_filename = "GCP_10002.xlsx"
    excel2table = Excel2Table(excel_filename=excel_filename)
    excel2table.extract_tables_from_excel()
