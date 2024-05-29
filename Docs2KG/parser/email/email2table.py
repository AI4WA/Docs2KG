import email
import os
import re

import pandas as pd


from Docs2KG.parser.email.base import EmailParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Email2Table(EmailParseBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables" / self.email_filename
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_tables_from_plain_text(self, text_content):
        # A simple regex-based example to find tables in plain text
        lines = text_content.splitlines()
        tables = []
        current_table = []
        for line in lines:
            if re.match(
                r"^\s*\S+", line
            ):  # This regex can be adjusted based on your table format
                current_table.append(line.split())
            else:
                if current_table:
                    tables.append(current_table)
                    current_table = []
        if current_table:
            tables.append(current_table)
        return tables

    def extract2table(self):

        with open(self.email_filepath, "rb") as f:
            msg = email.message_from_binary_file(f)

        table_index = 0

        for part in msg.walk():
            # content_type = part.get_content_type()

            # Handle HTML content
            # TODO: Not working as expected
            # if content_type == 'text/html':
            #     html_content = part.get_payload(decode=True)
            #     soup = BeautifulSoup(html_content, 'html.parser')
            #     tables = soup.find_all('table')
            #
            #     for table in tables:
            #         rows = table.find_all('tr')
            #         table_data = []
            #         for row in rows:
            #             cols = row.find_all(['td', 'th'])
            #             cols = [ele.get_text(strip=True) for ele in cols]
            #             table_data.append(cols)
            #
            #         # Convert to DataFrame
            #         df = pd.DataFrame(table_data)
            #
            #         # Save DataFrame to CSV
            #         csv_filename = os.path.join(self.table_output_dir, f'table_{table_index}.csv')
            #         df.to_csv(csv_filename, index=False, header=False, encoding='utf-8')
            #
            #         logger.info(f'Saved table to {csv_filename}')
            #         table_index += 1

            # Handle plain text content with potential tables
            # TODO: Not working as expected
            # if content_type == 'text/plain':
            #     text_content = part.get_payload(decode=True).decode('utf-8')
            #     tables = self.extract_tables_from_plain_text(text_content)
            #
            #     for table_data in tables:
            #         df = pd.DataFrame(table_data)
            #         csv_filename = os.path.join(self.table_output_dir, f'table_{table_index}.csv')
            #         df.to_csv(csv_filename, index=False, header=False, encoding='utf-8')
            #         logger.info(f'Saved plain text table to {csv_filename}')
            #         table_index += 1

            # Handle attachments
            # TODO: Haven't tested
            if part.get("Content-Disposition") and "attachment" in part.get(
                "Content-Disposition"
            ):
                filename = part.get_filename()
                if filename and (
                    filename.endswith(".csv")
                    or filename.endswith(".xls")
                    or filename.endswith(".xlsx")
                ):
                    attachment_data = part.get_payload(decode=True)
                    attachment_path = os.path.join(self.table_output_dir, filename)

                    with open(attachment_path, "wb") as f:
                        f.write(attachment_data)

                    if filename.endswith(".csv"):
                        df = pd.read_csv(attachment_path)
                    else:
                        df = pd.read_excel(attachment_path)

                    csv_filename = os.path.join(
                        self.table_output_dir, f"table_{table_index}.csv"
                    )
                    df.to_csv(csv_filename, index=False, encoding="utf-8")
                    logger.info(f"Saved attachment table to {csv_filename}")
                    table_index += 1
