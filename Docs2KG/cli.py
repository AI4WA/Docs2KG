import os
from pathlib import Path
from typing import Optional, Type

import click
from loguru import logger

from Docs2KG.digitization.image.pdf_docling import PDFDocling
from Docs2KG.digitization.native.ebook import EPUBDigitization
from Docs2KG.digitization.native.html_parser import HTMLDocling
from Docs2KG.digitization.native.word_docling import DOCXMammoth
from Docs2KG.kg_construction.layout_kg.layout_kg import LayoutKGConstruction
from Docs2KG.kg_construction.semantic_kg.ner.ner_prompt_based import (
    NERLLMPromptExtractor,
)
from Docs2KG.kg_construction.semantic_kg.ner.ner_spacy_match import NERSpacyMatcher
from Docs2KG.utils.config import PROJECT_CONFIG


class DocumentProcessor:
    PROCESSORS = {
        ".pdf": PDFDocling,
        ".docx": DOCXMammoth,
        ".html": HTMLDocling,
        ".epub": EPUBDigitization,
    }

    @classmethod
    def get_processor(cls, file_path: Path) -> Optional[Type]:
        """Get the appropriate processor for the file type."""
        return cls.PROCESSORS.get(file_path.suffix.lower())

    @classmethod
    def get_supported_formats(cls) -> str:
        """Get a string of supported file formats."""
        return ", ".join(cls.PROCESSORS.keys())


def setup_environment(config_path: str = None):
    """Setup the environment with the config file."""
    if config_path:
        os.environ["CONFIG_FILE"] = str(Path(config_path).resolve())
    else:
        os.environ["CONFIG_FILE"] = str(Path.cwd() / "config.yml")


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to the configuration file (default: ./config.yml)",
)
def cli(config):
    """Docs2KG - Document to Knowledge Graph conversion tool.

    Supports multiple document formats: PDF, DOCX, HTML, and EPUB.
    """
    setup_environment(config)
    logger.info(f"Using configuration: {os.environ.get('CONFIG_FILE')}")
    logger.info(PROJECT_CONFIG.data)


def process_single_file(
    file_path: Path, project_id: str, agent_name: str, agent_type: str
):
    """Process a single document file."""
    processor_class = DocumentProcessor.get_processor(file_path)
    if not processor_class:
        supported_formats = DocumentProcessor.get_supported_formats()
        raise click.ClickException(
            f"Unsupported file format: {file_path.suffix}. "
            f"Supported formats are: {supported_formats}"
        )

    # Step 1: Process document
    processor = processor_class(file_path=file_path)
    processor.process()

    # Step 2: Get markdown file path
    md_files = (
        PROJECT_CONFIG.data.output_dir
        / file_path.stem
        / processor_class.__name__
        / f"{file_path.stem}.md"
    )

    if not md_files.exists():
        logger.error(f"Markdown file not found: {md_files}")
        raise click.ClickException("Document processing failed")

    # Step 3: Construct Layout KG
    layout_kg_construction = LayoutKGConstruction(project_id)
    layout_kg_construction.construct(
        [{"content": md_files.read_text(), "filename": md_files.stem}]
    )

    # Step 4: Get JSON file path
    example_json = (
        PROJECT_CONFIG.data.output_dir
        / "projects"
        / project_id
        / "layout"
        / f"{file_path.stem}.json"
    )

    if not example_json.exists():
        logger.error(f"Layout KG JSON file not found: {example_json}")
        raise click.ClickException("Layout KG construction failed")

    # Step 5: Extract entities
    entity_extractor = NERSpacyMatcher(project_id)
    entity_extractor.construct_kg([example_json])

    # Step 6: Extract via prompt-based NER
    ner_extractor = NERLLMPromptExtractor(
        project_id=project_id, agent_name=agent_name, agent_type=agent_type
    )
    ner_extractor.construct_kg([example_json])

    logger.info(f"Successfully processed {file_path.name}")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--project-id",
    "-p",
    default="default",
    help="Project ID for the knowledge graph construction",
)
@click.option(
    "--agent-name",
    "-n",
    default="phi3.5",
    help="Name of the agent to use for NER extraction",
)
@click.option(
    "--agent-type",
    "-t",
    default="ollama",
    help="Type of the agent to use for NER extraction",
)
def process_document(file_path, project_id, agent_name, agent_type):
    """Process a single document file.

    FILE_PATH: Path to the document file (PDF, DOCX, HTML, or EPUB)
    """
    file_path = Path(file_path)
    logger.info(f"Processing document: {file_path}")
    process_single_file(file_path, project_id, agent_name, agent_type)


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True))
@click.option(
    "--project-id",
    "-p",
    default="default",
    help="Project ID for the knowledge graph construction",
)
@click.option(
    "--formats",
    "-f",
    help='Comma-separated list of file formats to process (e.g., "pdf,docx,html")',
)
@click.option(
    "--agent-name",
    "-n",
    default="phi3.5",
    help="Name of the agent to use for NER extraction",
)
@click.option(
    "--agent-type",
    "-t",
    default="ollama",
    help="Type of the agent to use for NER extraction",
)
def batch_process(input_dir, project_id, formats, agent_name, agent_type):
    """Process all supported documents in a directory.

    INPUT_DIR: Directory containing documents to process
    """
    input_dir = Path(input_dir)

    # Filter formats if specified
    if formats:
        allowed_formats = {f".{fmt.lower().strip()}" for fmt in formats.split(",")}
        supported_formats = set(DocumentProcessor.PROCESSORS.keys())
        invalid_formats = allowed_formats - supported_formats
        if invalid_formats:
            raise click.ClickException(
                f"Unsupported format(s): {', '.join(invalid_formats)}. "
                f"Supported formats are: {DocumentProcessor.get_supported_formats()}"
            )
    else:
        allowed_formats = set(DocumentProcessor.PROCESSORS.keys())

    # Find all files with supported extensions
    files_to_process = []
    for ext in allowed_formats:
        files_to_process.extend(input_dir.glob(f"*{ext}"))

    if not files_to_process:
        logger.warning(
            f"No supported documents found in {input_dir}. "
            f"Looking for: {', '.join(allowed_formats)}"
        )
        return

    logger.info(f"Found {len(files_to_process)} documents to process")

    for file_path in files_to_process:
        try:
            process_single_file(file_path, project_id, agent_name, agent_type)
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            continue

    logger.info("Batch processing completed")


@cli.command()
def list_formats():
    """List all supported document formats."""
    supported_formats = DocumentProcessor.get_supported_formats()
    click.echo(f"Supported document formats: {supported_formats}")


if __name__ == "__main__":
    cli()
