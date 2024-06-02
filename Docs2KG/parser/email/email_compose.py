import email
import json

import pandas as pd

from Docs2KG.parser.email.base import EmailParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class EmailDecompose(EmailParseBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_output_dir = self.output_dir / "images"
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_output_dir = self.output_dir / "attachments"
        self.attachments_output_dir.mkdir(parents=True, exist_ok=True)

    def decompose_email(self):
        """
        Decompose the email file to images, attachments, and metadata
        """
        msg = self.read_email_file()
        self.download_email_attachment(msg)
        return msg

    def read_email_file(self):
        with open(self.email_file, "rb") as f:
            msg = email.message_from_bytes(f.read())
        return msg

    def download_email_attachment(self, msg):
        """
        Download the email attachment and save it to the output directory
        Args:
            msg:

        Returns:

        """
        images = []
        attachments = []
        # extract all the attachments
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    filename = self.clean_filename(filename, part)

                    filepath = self.attachments_output_dir / filename
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    attachments.append(
                        {
                            "name": filename,
                            "path": filepath,
                            "original_filename": part.get_filename(),
                        }
                    )
            # if content type is image/ , download the image
            if part.get_content_type().startswith("image/"):
                img_data = part.get_payload(decode=True)
                img_name = part.get_filename()
                if img_name:
                    img_name = self.clean_filename(img_name, part)
                    img_path = self.image_output_dir / img_name
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    logger.info(f"Saved image to: {img_path}")
                    images.append(
                        {
                            "name": img_name,
                            "path": img_path,
                            "cid": part.get("Content-ID", ""),
                        }
                    )
            # save content to html or text, end with .html or .txt
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True)
                html_output = self.output_dir / "email.html"
                with open(html_output, "wb") as f:
                    f.write(html_content)
                logger.info(f"Saved html to: {html_output}")
            if part.get_content_type() == "text/plain":
                text_content = part.get_payload(decode=True)
                text_output = self.output_dir / "email.txt"
                with open(text_output, "wb") as f:
                    f.write(text_content)
                logger.info(f"Saved text to: {text_output}")

            # save df to csv, end with .csv

        # metadata to json, include subject, from, to, date
        email_metadata = {
            "subject": msg["subject"],
            "from": msg["from"],
            "to": msg["to"],
            "date": msg["date"],
        }
        metadata_output = self.output_dir / "metadata.json"
        with open(metadata_output, "w") as f:
            json.dump(email_metadata, f)

        images_df = pd.DataFrame(images)
        images_output = self.image_output_dir / "images.csv"
        images_df.to_csv(images_output, index=False)

        attachments_df = pd.DataFrame(attachments)
        attachments_output = self.attachments_output_dir / "attachments.csv"
        attachments_df.to_csv(attachments_output, index=False)

        return msg

    @staticmethod
    def clean_filename(filename: str, part):
        """
        Clean the filename to remove special characters.

        Args:
            filename (str): Filename to clean.
            part (email.message.Message): Email part.

        Returns:
            str: Cleaned filename.
        """
        if "?=" in filename:
            filename = filename.rsplit("?=", 1)[0]
        if part.get("Content-ID"):
            filename = f"{part.get('Content-ID')}_{filename}"
        return filename
