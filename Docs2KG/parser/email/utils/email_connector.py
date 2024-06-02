import email
import imaplib
import json

from Docs2KG.utils.constants import DATA_INPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class EmailConnector:
    """
    Login to the email server to download emails with keywords, or download specific number of latest emails
    """

    def __init__(
        self,
        email_address,
        password,
        output_dir=None,
        search_keyword: str = None,
        num_emails: int = 50,
        imap_server: str = "imap.gmail.com",
        imap_port: int = 993,
    ):
        """
        Initialize the EmailConnector with login credentials and search parameters.

        Args:
            email_address (str): Email address to log in.
            password (str): Password for the email address.
            search_keyword (str, optional): Keyword to search emails. Defaults to None.
            num_emails (int, optional): Number of latest emails to download. Defaults to 50.
        """
        self.email_address = email_address
        self.password = password
        self.search_keyword = search_keyword
        self.num_emails = num_emails
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.imap = None
        self.login_imap()
        self.output_dir = output_dir
        if output_dir is None:
            self.output_dir = DATA_INPUT_DIR / "email" / email_address
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def login_imap(self):
        """
        Login to the IMAP server.

        """
        self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        self.imap.login(self.email_address, self.password)
        # log whether login was successful
        if self.imap.state == "AUTH":
            logger.info("Login successful")
        else:
            logger.error("Login failed")
            raise Exception("Login failed")

    def pull(self):
        """
        Pull the emails from the email server.
        """
        logger.info("Pulling emails")
        logger.info(self.search_keyword)
        if self.search_keyword:
            email_ids = self.search_emails()
        else:
            email_ids = self.download_latest_emails()

        for email_id in email_ids:
            logger.info(f"Downloading email: {email_id}")
            self.download_email(email_id)

    def search_emails(self):
        """
        Search for emails based on the search keyword.

        Returns:
            list: List of email IDs that match the search criteria.
        """
        self.imap.select("inbox")
        if self.search_keyword:
            result, data = self.imap.search(None, f'(BODY "{self.search_keyword}")')
            logger.info(f"Number of emails found: {len(data[0].split())}")
            logger.info(f"Email IDs: {data[0].split()}")
        else:
            result, data = self.imap.search(None, "ALL")
        email_ids = data[0].split()
        return email_ids

    def fetch_emails(self, email_ids):
        """
        Fetch the emails based on email IDs.

        Args:
            email_ids (list): List of email IDs to fetch.

        Returns:
            list: List of email messages.
        """
        emails = []
        for email_id in email_ids:
            result, data = self.imap.fetch(email_id, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            emails.append(msg)
        return emails

    def download_latest_emails(self):
        """
        Download the latest emails up to the specified number.

        Returns:
            list: List of the latest email messages.
        """
        email_ids = self.search_emails()
        latest_email_ids = email_ids[-self.num_emails :]
        latest_emails = self.fetch_emails(latest_email_ids)
        return latest_emails

    def download_email(self, email_id):
        """
        Download a specific email based on the email ID.

        Args:
            email_id (str): Email ID to download.

        Returns:
            email.message.Message: Email message.
        """
        # fetch the email for the content and all the attachments
        result, data = self.imap.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        # save the email to folder with email_id as filename
        email_output_dir = self.output_dir / email_id.decode("utf-8")
        email_output_dir.mkdir(parents=True, exist_ok=True)
        email_filepath = email_output_dir / "email.eml"
        with open(email_filepath, "wb") as f:
            f.write(raw_email)

        # extract all the attachments
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    if filename.endswith("?="):
                        filename = filename.rsplit("?=", 1)[0]

                    filepath = email_output_dir / filename
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
            # if content type is image/ , download the image
            if part.get_content_type().startswith("image/"):
                img_data = part.get_payload(decode=True)
                img_name = part.get_filename()
                if img_name:
                    if img_name.endswith("?="):
                        img_name = img_name.rsplit("?=", 1)[0]
                    img_path = email_output_dir / img_name

                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    logger.info(f"Saved image to: {img_path}")
            # save content to html or text, end with .html or .txt
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True)
                html_output = email_output_dir / "email.html"
                with open(html_output, "wb") as f:
                    f.write(html_content)
                logger.info(f"Saved html to: {html_output}")
            if part.get_content_type() == "text/plain":
                text_content = part.get_payload(decode=True)
                text_output = email_output_dir / "email.txt"
                with open(text_output, "wb") as f:
                    f.write(text_content)
                logger.info(f"Saved text to: {text_output}")

        # metadata to json, include subject, from, to, date
        email_metadata = {
            "subject": msg["subject"],
            "from": msg["from"],
            "to": msg["to"],
            "date": msg["date"],
        }
        metadata_output = email_output_dir / "metadata.json"
        with open(metadata_output, "w") as f:
            json.dump(email_metadata, f)

        return msg

    def logout(self):
        """
        Logout from the email servers.
        """
        if self.imap:
            self.imap.logout()
