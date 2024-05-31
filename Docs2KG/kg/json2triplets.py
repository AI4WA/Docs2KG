import json
from pathlib import Path

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class JSON2Triplets:
    """
    Convert JSON to triplets

    A JSON for all nodes:

    {
        "nodes": [
            {
                "uuid": uuid1
                "labels": ["label1", "label2"],
                "properties": {
                    "prop1": "value1",
                    "prop2": "value2"
                }
            },
            {
                "uuid": uuid2
                "labels": ["label3"],
                "properties": {
                    "prop3": "value3",
                    "prop4": "value4"
                }
            }
        ],
        "relationships": [
            {

                "start_node": uuid1,
                "end_node": uuid2,
                "type": "type1",
                "properties": {
                    "prop5": "value5",
                    "prop6": "value6"
                }
            }
        ]
    }


    """

    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.kg_folder = folder_path / "kg"
        self.kg_json = self.load_kg()
        self.triplets_json = {"nodes": [], "relationships": []}

    def load_kg(self) -> dict:
        """
        Load the layout knowledge graph from JSON
        """
        with open(self.kg_folder / "layout_kg.json", "r") as f:
            kg_json = json.load(f)
        return kg_json

    def transform(self):
        """
        Transform the JSON to triplets
        """
        self.transform_node(self.kg_json)
        self.export_json()

    def transform_node(self, node: dict, parent_uuid: str = None):
        """
        Transform the node to triplets

        Args:
            node (dict): The node
            parent_uuid (str): The UUID of the node

        Returns:

        """
        labels = [node["node_type"]]
        uuid = node["uuid"]
        properties = node["node_properties"]
        entity = {"uuid": uuid, "labels": labels, "properties": properties}
        self.triplets_json["nodes"].append(entity)
        rel = {
            "start_node": parent_uuid,
            "end_node": uuid,
            "type": "HAS_CHILD",
        }
        self.triplets_json["relationships"].append(rel)
        for child in node["children"]:
            self.transform_node(child, parent_uuid=uuid)

    def export_json(self):
        """
        Export the triplets JSON
        """
        # how many nodes
        logger.info(f"Number of nodes: {len(self.triplets_json['nodes'])}")
        # how many relationships
        logger.info(
            f"Number of relationships: {len(self.triplets_json['relationships'])}"
        )
        with open(self.kg_folder / "triplets_kg.json", "w") as f:
            json.dump(self.triplets_json, f, indent=4)
        logger.info(f"Triplets JSON exported to {self.kg_folder / 'triplets_kg.json'}")
