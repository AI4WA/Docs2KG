from Docs2KG.parser.email.email2images import Email2Images
from Docs2KG.parser.email.email2markdown import Email2Markdown
from Docs2KG.utils.constants import DATA_INPUT_DIR


if __name__ == "__main__":
    email_filename = DATA_INPUT_DIR / "email" / "email.eml"
    email2md = Email2Markdown(email_filename=email_filename)
    email2md.convert2markdown()
    email2images = Email2Images(email_filename=email_filename)
    email2images.extract2images()
