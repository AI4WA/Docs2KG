"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

root = Path(__file__).parent.parent
src = root / "Docs2KG"

for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    full_doc_path = "sources" / module_path.with_suffix(".md")

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        continue
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print(f"::: Docs2KG.{identifier}", file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))


src = root / "examples"

# Loop through all .py files in the source directory
for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    full_doc_path = Path("examples") / module_path.with_suffix(".md")

    parts = tuple(module_path.parts)

    # Skip __init__.py files
    if parts[-1] == "__init__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:

        fd.write("## Code Example\n\n")
        fd.write("```python\n")
        with open(path) as main_file:
            fd.write(main_file.read())
        fd.write("\n```\n")

        identifier = ".".join(parts)
        print(f"::: examples.{identifier}", file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))
