from Docs2KG.parser.email.email_compose import EmailDecompose
from Docs2KG.utils.constants import DATA_INPUT_DIR

if __name__ == "__main__":
    email_filename = DATA_INPUT_DIR / "email.eml"
    email_decomposer = EmailDecompose(email_file=email_filename)
    email_decomposer.decompose_email()
