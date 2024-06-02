# Tutorial

::: Docs2KG

Business Scenario: Real Estate Market Analysis

Objective:
Demonstrate how the project can extract content from various sources (web pages, Excel files, emails), generate a unified knowledge graph, and provide advanced capabilities such as entity search and question answering. The scenario focuses on analyzing the office market data and providing actionable insights to a real estate client.

Scenario:
You are a real estate consultant providing insights to a client interested in the current and projected office market trends for 2024. The client wants to understand the market dynamics, trends, and key statistics to make informed decisions about investments and office space management.

Data Sources:

    Web Page: Market report from the Property Council of Australia.
        URL: https://www.propertycouncil.com.au/news-research/research/office-market-report
    PDF Document: Office market analysis report, which is in directory data/input/market_report.pdf.    
    Excel File: Office market statistics for 2024, which is in directory data/input/market_report.xlsx.    
    Email: Summary of the office market report.
    

## Steps to Demonstrate:
### 1. Data Extraction:
    Extract content from the provided web page, Excel file, and email.
    Extracted content includes text, images, tables, and structured data in JSON format.
```sh
from Docs2KG.kg.web_layout_kg import WebLayoutKG
from Docs2KG.kg.semantic_kg import SemanticKG
from Docs2KG.kg.utils.json2triplets import JSON2Triplets
from Docs2KG.kg.utils.neo4j_connector import Neo4jLoader

# Extract data from the web page
url = "https://www.propertycouncil.com.au/news-research/research/office-market-report"
web_layout_kg = WebLayoutKG(url=url)
web_layout_kg.create_kg()

# Extract data from the Excel file (assuming a similar class exists for Excel extraction)
from Docs2KG.kg.excel_layout_kg import ExcelLayoutKG
excel_file = "data/input/office_market_2024.xlsx"
excel_layout_kg = ExcelLayoutKG(excel_file=excel_file)
excel_layout_kg.create_kg()

# Extract data from the email (assuming a similar class exists for email extraction)
from Docs2KG.kg.email_layout_kg import EmailLayoutKG
email_file = "data/input/report_summary.eml"
email_layout_kg = EmailLayoutKG(email_file=email_file)
email_layout_kg.create_kg()


# Extract data from the PDF file
from Docs2KG.parser.pdf.pdf2metadata import get_scanned_or_exported, PDF_TYPE_SCANNED
from Docs2KG.parser.pdf.pdf2blocks import PDF2Blocks
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.modules.llm.markdown2json import LLMMarkdown2Json

pdf_file = 'data/input/OMR241-Chartbook.pdf'
output_folder = 'data/output/market_report'

scanned_or_exported = get_scanned_or_exported(pdf_file)
if scanned_or_exported == PDF_TYPE_SCANNED:
    pdf2tables = PDF2Tables(pdf_file)
    pdf2tables.extract2tables(output_csv=True)
else:
    pdf_2_blocks = PDF2Blocks(pdf_file)
    blocks_dict = pdf_2_blocks.extract_df(output_csv=True)

    pdf_to_text = PDF2Text(pdf_file)
    text = pdf_to_text.extract2text(output_csv=True)
    md_text = pdf_to_text.extract2markdown(output_csv=True)

    input_md_file = output_folder + "/texts/md.csv"
    markdown2json = LLMMarkdown2Json(input_md_file, llm_model_name="gpt-3.5-turbo")
    markdown2json.extract2json()


```
### 2. Generate Unified Knowledge Graph:
    Combine the extracted data into a unified knowledge graph.
    Incorporate semantic relationships using NLP models.
```sh
# Combine and process the extracted data
semantic_kg_web = SemanticKG(folder_path=web_layout_kg.output_dir, input_format="html", llm_enabled=True)
semantic_kg_web.add_semantic_kg()

semantic_kg_excel = SemanticKG(folder_path=excel_layout_kg.output_dir, input_format="excel", llm_enabled=True)
semantic_kg_excel.add_semantic_kg()

semantic_kg_email = SemanticKG(folder_path=email_layout_kg.output_dir, input_format="email", llm_enabled=True)
semantic_kg_email.add_semantic_kg()

semantic_kg_pdf = SemanticKG(folder_path=output_folder, input_format="pdf", llm_enabled=True)
semantic_kg_pdf.add_semantic_kg()

# Transform JSON to triplets for Neo4j loading
json_2_triplets_web = JSON2Triplets(web_layout_kg.output_dir)
json_2_triplets_web.transform()

json_2_triplets_excel = JSON2Triplets(excel_layout_kg.output_dir)
json_2_triplets_excel.transform()

json_2_triplets_email = JSON2Triplets(email_layout_kg.output_dir)
json_2_triplets_email.transform()

json_2_triplets_pdf = JSON2Triplets(output_folder)
json_2_triplets_pdf.transform()

```

### 3. Load Data into Neo4j:
Load the knowledge graph data into Neo4j for querying.
```sh
# Load data into Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "testpassword"

neo4j_loader_web = Neo4jLoader(uri, username, password, web_layout_kg.output_dir / "kg" / "triplets_kg.json", clean=True)
neo4j_loader_web.load_data()

neo4j_loader_excel = Neo4jLoader(uri, username, password, excel_layout_kg.output_dir / "kg" / "triplets_kg.json", clean=True)
neo4j_loader_excel.load_data()

neo4j_loader_email = Neo4jLoader(uri, username, password, email_layout_kg.output_dir / "kg" / "triplets_kg.json", clean=True)
neo4j_loader_email.load_data()

neo4j_loader_pdf = Neo4jLoader(uri, username, password, output_folder / "kg" / "triplets_kg.json", clean=True)
neo4j_loader_pdf.load_data()

neo4j_loader_web.close()
neo4j_loader_excel.close()
neo4j_loader_email.close()
neo4j_loader_pdf.close()

```

### 4. Entity Search and Question Answering:
    Demonstrate entity search capabilities.
    Answer specific questions about the office market using the knowledge graph.

```sh
from py2neo import Graph

# Connect to Neo4j
graph = Graph(uri, auth=(username, password))

# Example queries
entity_query = "MATCH (e:Entity) WHERE e.name = 'Office Market' RETURN e"
question_query = """
MATCH (e:Entity)-[r:RELATED_TO]->(o:OfficeMarket)
WHERE e.name = '2024 Statistics'
RETURN o
"""

# Execute queries
entity_result = graph.run(entity_query).data()
question_result = graph.run(question_query).data()

print("Entity Search Result:", entity_result)
print("Question Answering Result:", question_result)
```