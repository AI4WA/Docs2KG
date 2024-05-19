from Docs2KG.parser.email.email2images import Email2Images
from Docs2KG.parser.email.email2markdown import Email2Markdown
from Docs2KG.parser.email.email2table import Email2Table

if __name__ == "__main__":
    email_filename = "UWA Sport eNews _ April 2024.eml"
    email2md = Email2Markdown(email_filename=email_filename)
    email2md.convert2markdown()
    email2images = Email2Images(email_filename=email_filename)
    email2images.extract2images()
    # email2table = Email2Table(email_filename=email_filename)
    # email2table.extract2table()
