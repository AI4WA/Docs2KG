from email import policy
from email.parser import BytesParser

from Docs2KG.parser.email.base import EmailParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

class Email2Markdown(EmailParseBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_output_dir = self.output_dir / "markdowns"
        self.markdown_output_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_filepath = f"{self.markdown_output_dir}/{self.email_filename.split('.')[0] + '.md'}"


    def convert2markdown(self):
        """
        Convert the email file to markdown and save it to the output directory
        """
        logger.info(f"Converting the email file from {self.email_filename} to markdown...")
        with open(self.email_filepath, 'rb') as eml_file:
            msg = BytesParser(policy=policy.default).parse(eml_file)
            from_ = msg['From']
            to = msg['To']
            subject = msg['Subject']
            date = msg['Date']

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    # Extract text/plain parts
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode(part.get_content_charset())
            else:
                # If not multipart, the payload is the message body
                body = msg.get_payload(decode=True).decode(msg.get_content_charset())

            markdown_content = f"""### From: {from_}\n\n### To: {to}\n\n### Subject: {subject}\n\n### Date: {date}\n\n---\n\n{body}"""
            with open(self.markdown_filepath, 'w') as markdown_file:
                markdown_file.write(markdown_content)
            logger.info(f"Converted!")
