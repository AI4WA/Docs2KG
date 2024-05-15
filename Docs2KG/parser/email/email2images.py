import email
import os
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from Docs2KG.parser.email.base import EmailParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

class Email2Images(EmailParseBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_output_dir = self.output_dir / "images" / self.email_filename
        self.image_output_dir.mkdir(parents=True, exist_ok=True)


    def extract2images(self):
        """
        Extract images from the email file and save them to the output directory
        """


        with open(self.email_filepath, 'rb') as f:
            msg = email.message_from_binary_file(f)

        for part in msg.walk():
            # Extract attachments
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()

                # Check if the attachment is an image
                if filename and any(filename.lower().endswith(ext) for ext in ['jpg', 'jpeg', 'png', 'gif']):
                    filepath = os.path.join(self.image_output_dir, filename)

                    # Save the image
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    logger.info(f'Saved: {filepath}')

            # Extract image links from HTML content
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True)

                soup = BeautifulSoup(html_content, 'html.parser')
                img_tags = soup.find_all('img')
                for img_tag in img_tags:
                    img_url = img_tag.get('src')

                    if img_url:
                        try:
                            img_data = requests.get(img_url).content
                            img_name = quote(img_url, '')
                            img_path = os.path.join(self.image_output_dir, img_name)
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            logger.info(f'Saved image to: {img_path}')
                        except requests.RequestException as e:
                            logger.info(f'Could not download image {img_url}: {e}')
