import json
from pathlib import Path

from Docs2KG.utils.constants import DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class ExcelParseBase:
    def __init__(self, excel_file: Path, output_dir: Path = None):
        """
        Initialize the ExcelParseBase class

        Args:
            excel_file (Path): Path to the excel file
            output_dir (Path): Path to the output directory where the converted files will be saved

        """
        self.excel_file = excel_file

        self.output_dir = output_dir
        if self.output_dir is None:
            excel_output_folder = DATA_OUTPUT_DIR / self.excel_file.name
            excel_output_folder.mkdir(parents=True, exist_ok=True)
            self.output_dir = excel_output_folder

        # export excel metadata
        self.metadata = self.output_dir / "metadata.json"
        from openpyxl import load_workbook

        wb = load_workbook(self.excel_file)
        properties = wb.properties
        metadata_dict = {
            "filename": self.excel_file.name,
            "title": properties.title,
            "subject": properties.subject,
            "creator": properties.creator,
            "keywords": properties.keywords,
            "description": properties.description,
            "lastModifiedBy": properties.lastModifiedBy,
            "revision": properties.revision,
            "created": properties.created.isoformat() if properties.created else None,
            "modified": (
                properties.modified.isoformat() if properties.modified else None
            ),
            "lastPrinted": (
                properties.lastPrinted.isoformat() if properties.lastPrinted else None
            ),
            "category": properties.category,
            "contentStatus": properties.contentStatus,
            "identifier": properties.identifier,
            "language": properties.language,
            "version": properties.version,
        }

        metadata_json = json.dumps(metadata_dict, indent=4)

        with open(self.metadata, "w") as f:
            f.write(metadata_json)
