import json
from pathlib import Path
from uuid import uuid4

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
        self.entities_mapping = {}

    def transform(self):
        """
        Transform the JSON to triplets
        """
        self.transform_node(self.kg_json)
        self.transform_images()
        self.transform_tables()
        self.transform_text2kg(self.kg_json)
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

    def transform_images(self):
        """
        Connect the image to nearby text
        """
        for page in self.kg_json["children"]:
            for node in page["children"]:
                if node["node_type"] == "image":
                    image_uuid = node["uuid"]
                    # add text_block node and relationship
                    # first add where the image is mentioned
                    mentioned_in = node["node_properties"].get("mentioned_in", [])
                    for mention_uuid in mentioned_in:
                        mention_rel = {
                            "start_node": image_uuid,
                            "end_node": mention_uuid,
                            "type": "MENTIONED_IN",
                        }
                        self.triplets_json["relationships"].append(mention_rel)
                    if "children" not in node:
                        continue
                    # then add the nearby text block
                    for child in node["children"]:
                        if child["node_type"] == "text_block":
                            text_block_uuid = child["uuid"]
                            self.triplets_json["nodes"].append(
                                {
                                    "uuid": text_block_uuid,
                                    "labels": ["text_block"],
                                    "properties": child["node_properties"],
                                }
                            )

                            rel = {
                                "start_node": image_uuid,
                                "end_node": text_block_uuid,
                                "type": "NEARBY_TEXT",
                            }
                            self.triplets_json["relationships"].append(rel)
                            # include where the text block belong to the tree
                            text_block_linkage = child.get("linkage", [])
                            for linkage_uuid in text_block_linkage:
                                linkage_rel = {
                                    "start_node": text_block_uuid,
                                    "end_node": linkage_uuid,
                                    "type": "TEXT_LINKAGE",
                                }
                                self.triplets_json["relationships"].append(linkage_rel)

    def transform_tables(self):
        """
        This is to transform the text into a format can be used in neo4j, etc.
        Returns:

        """

        for page in self.kg_json["children"]:
            for node in page["children"]:
                if node["node_type"] == "table_csv":
                    table_uuid = node["uuid"]
                    # add text_block node and relationship
                    # first add where the table is mentioned
                    mentioned_in = node["node_properties"].get("mentioned_in", [])
                    for mention_uuid in mentioned_in:
                        mention_rel = {
                            "start_node": table_uuid,
                            "end_node": mention_uuid,
                            "type": "MENTIONED_IN",
                        }
                        self.triplets_json["relationships"].append(mention_rel)
                    if "children" not in node:
                        continue
                    # then add the nearby text block
                    for child in node["children"]:
                        if child["node_type"] == "text_block":
                            text_block_uuid = child["uuid"]
                            self.triplets_json["nodes"].append(
                                {
                                    "uuid": text_block_uuid,
                                    "labels": ["text_block"],
                                    "properties": child["node_properties"],
                                }
                            )

                            rel = {
                                "start_node": table_uuid,
                                "end_node": text_block_uuid,
                                "type": "NEARBY_TEXT",
                            }
                            self.triplets_json["relationships"].append(rel)
                            # include where the text block belong to the tree
                            text_block_linkage = child.get("linkage", [])
                            for linkage_uuid in text_block_linkage:
                                linkage_rel = {
                                    "start_node": text_block_uuid,
                                    "end_node": linkage_uuid,
                                    "type": "TEXT_LINKAGE",
                                }
                                self.triplets_json["relationships"].append(linkage_rel)

    def transform_text2kg(self, node: dict):
        """

        Loop through the kg, and then figure out the Text2KG part, get them into the triplets

        However, before that we will need to give each Text2KG node an uuid
        And if they are the same content, they should have the same uuid

        Returns:

        """
        for child in node["children"]:
            if "children" in child:
                self.transform_text2kg(child)
            text2kg_list = child["node_properties"].get("text2kg", [])
            if len(text2kg_list) == 0:
                continue
            for text2kg in text2kg_list:
                logger.info(f"Text2KG: {text2kg}")
                subject = text2kg.get("subject", None)
                subject_ner_type = text2kg.get("subject_ner_type", None)
                predicate = text2kg.get("predicate", None)
                object_ent = text2kg.get("object", None)
                object_ner_type = text2kg.get("object_ner_type", None)
                if any(
                    [
                        subject is None,
                        predicate is None,
                        object_ent is None,
                        subject_ner_type is None,
                        object_ner_type is None,
                        subject == "",
                        object_ent == "",
                        predicate == "",
                    ]
                ):
                    continue
                # check if the subject is in the entities_mapping
                if subject not in self.entities_mapping:
                    self.entities_mapping[subject] = str(uuid4())
                if object_ent not in self.entities_mapping:
                    self.entities_mapping[object_ent] = str(uuid4())
                subject_uuid = self.entities_mapping[subject]
                object_uuid = self.entities_mapping[object_ent]
                # add the subject
                self.triplets_json["nodes"].append(
                    {
                        "uuid": subject_uuid,
                        "labels": ["entity", subject_ner_type, "TEXT2KG"],
                        "properties": {"text": subject},
                    }
                )
                # add the object
                self.triplets_json["nodes"].append(
                    {
                        "uuid": object_uuid,
                        "labels": ["entity", object_ner_type, "TEXT2KG"],
                        "properties": {"text": object_ent},
                    }
                )
                # add the relationship
                rel = {
                    "start_node": subject_uuid,
                    "end_node": object_uuid,
                    "type": predicate,
                    "properties": {"source": "TEXT2KG"},
                }
                self.triplets_json["relationships"].append(rel)

    def load_kg(self) -> dict:
        """
        Load the layout knowledge graph from JSON
        """
        with open(self.kg_folder / "layout_kg.json", "r") as f:
            kg_json = json.load(f)
        return kg_json

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
