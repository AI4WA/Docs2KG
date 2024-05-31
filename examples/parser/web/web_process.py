from Docs2KG.parser.web.web2images import Web2Images
from Docs2KG.parser.web.web2markdown import Web2Markdown
from Docs2KG.parser.web.web2tables import Web2Tables
from Docs2KG.parser.web.web2urls import Web2URLs

if __name__ == "__main__":
    url = "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA57080"
    web_2_md = Web2Markdown(url=url)
    web_2_images = Web2Images(url=url)
    web_2_tables = Web2Tables(url=url)
    web_2_urls = Web2URLs(url=url)

    web_2_md.convert2markdown()
    web_2_images.extract2images()
    web_2_tables.extract2tables()
    web_2_urls.extract2tables()
