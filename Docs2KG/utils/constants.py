from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().resolve().parents[2]

DATA_DIR = PROJECT_DIR / "data"
DOC_DIR = PROJECT_DIR / "docs"

DATA_INPUT_DIR = DATA_DIR / "input"
DATA_OUTPUT_DIR = DATA_DIR / "output"

# if not exists, create the directories
DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_INPUT_DIR.mkdir(parents=True, exist_ok=True)
