import argparse
from pathlib import Path

from Docs2KG.kg.dynamic_schema import DynamicSchema
from Docs2KG.utils.constants import DATA_OUTPUT_DIR

if __name__ == "__main__":
    """
    1. From the generated KG, how can we do the schema merge?
        - You can hook this into the neo4j after the KG is loaded
    2. Human in the loop for the schema merge
    """
    args = argparse.ArgumentParser()
    args.add_argument(
        "--kg_json_file",
        type=str,
        default=None,
        help="The KG JSON File Absolute Path",
    )
    args.add_argument(
        "--kg_json", type=str, default=None, help="The KG JSON File Absolute Path"
    )

    args = args.parse_args()

    if not args.kg_json_file:
        kg_json_file = (
            DATA_OUTPUT_DIR / "Excellent_Example_Report.pdf" / "kg" / "triplets_kg.json"
        )
    else:
        kg_json_file = Path(args.kg_json_file)
    dynamic_schema = DynamicSchema(kg_json_file=kg_json_file)
    dynamic_schema.schema_extraction()
    dynamic_schema.schema_freq_merge()
    dynamic_schema.schema_similarity_merge()
    dynamic_schema.human_in_the_loop_input()
