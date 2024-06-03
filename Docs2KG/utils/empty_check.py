from pathlib import Path


def empty_check(path: Path) -> bool:
    with open(path, "r") as f:
        content = f.read().strip()
    return content == ""
