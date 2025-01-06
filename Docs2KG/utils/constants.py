from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().resolve().parents[2]

DATA_DIR = PROJECT_DIR / "data"
DOC_DIR = PROJECT_DIR / "docs"


# these are the default directories for input and output data
DATA_INPUT_DIR = DATA_DIR / "input"
DATA_OUTPUT_DIR = DATA_DIR / "output"
DATA_ONTOLOGY_DIR = DATA_DIR / "ontology"

DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_INPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_ONTOLOGY_DIR.mkdir(parents=True, exist_ok=True)
