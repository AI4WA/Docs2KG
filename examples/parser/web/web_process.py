from Docs2KG.parser.web.web2images import Web2Images
from Docs2KG.parser.web.web2markdown import Web2Markdown
from Docs2KG.parser.web.web2tables import Web2Tables

if __name__ == "__main__":
    url = "https://abs.gov.au/census/find-census-data/quickstats/2021/LGA57080"
    web2md = Web2Markdown(urls=[url])
    web2imgs = Web2Images(urls=[url])
    web2tables = Web2Tables(urls=[url])

    web2md.batch_download()

    web2md.batch_convert2markdown()
    web2imgs.batch_extract2images()
    web2tables.batch_extract2tables()
