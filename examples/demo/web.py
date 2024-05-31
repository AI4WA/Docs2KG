from Docs2KG.kg.web_layout_kg import WebLayoutKG

if __name__ == "__main__":
    """
    Extract the HTML file to images, markdown, tables, and urls and save it to the output directory

    1. Get html, images, markdown, tables, and urls from the given URL
    """
    url = "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA57080"

    web_layout_kg = WebLayoutKG(url=url)
    web_layout_kg.create_kg()
