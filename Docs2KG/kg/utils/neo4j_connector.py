import json
from pathlib import Path

from neo4j import GraphDatabase
from tqdm import tqdm

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Neo4jLoader:
    def __init__(
        self,
        uri: str,
        username: str,
        password: str,
        json_file_path: Path,
        clean: bool = False,
    ):
        """

        Args:
            uri (str): URI of the Neo4j database
            username (str): Username of the Neo4j database
            password (str): Password of the Neo4j database
            json_file_path (Path): Path to the JSON file containing the data
            clean (bool): Whether to clean the database before loading the data
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.json_file_path = json_file_path
        self.driver = GraphDatabase.driver(
            self.uri, auth=(self.username, self.password)
        )
        self.clean = clean

        if self.clean:
            self.clean_database()

    def clean_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleaned successfully")

    def close(self):
        self.driver.close()

    def load_json_data(self):
        with open(self.json_file_path, "r") as file:
            return json.load(file)

    def load_nodes(self, nodes):
        """
        It can be any type of node, not just Person

        One example node is like this:

        ```
           {
            "uuid": "6cedef4a-52d1-4ff2-8fc8-644ad5de8c49",
            "labels": [
                "text_block"
            ],
            "properties": {
                "text_block_bbox": "(373.5598449707031, 667.95703125, 490.0483093261719, 679.9588623046875)",
                "content": "B.Sc., Geol, Grad Dip (GIS) ",
                "position": "right",
                "text_block_number": 9,
                "text2kg": [
                    {
                        "subject": "B.Sc.",
                        "subject_ner_type": "Degree",
                        "predicate": "has",
                        "object": "Geol",
                        "object_ner_type": "Subject"
                    },
                    {
                        "subject": "B.Sc.",
                        "subject_ner_type": "Degree",
                        "predicate": "has",
                        "object": "Grad Dip (GIS)",
                        "object_ner_type": "Certificate"
                    }
                ]
            }
        }
        ```

        Args:
            nodes:

        Returns:

        """
        for node in tqdm(nodes, desc="Loading Nodes"):
            labels = ":".join(node["labels"])
            properties = node["properties"]

            properties["uuid"] = node["uuid"]
            properties["labels"] = labels

            # if the value of the property is a dictionary or a list, remove it
            keys_to_remove = [
                key
                for key, value in properties.items()
                if isinstance(value, (dict, list))
            ]
            for key in keys_to_remove:
                properties.pop(key)

            properties_query = ", ".join(
                [
                    f"{key.replace('.', '_')}: ${key}"
                    for key in node["properties"].keys()
                ]
            )
            node_query = f"""
              CREATE (n:{labels} {{ {properties_query} }})
            """
            logger.debug(node_query)
            logger.debug(properties)

            with self.driver.session() as session:
                session.run(node_query, **properties)

    def load_relationships(self, relationships):
        """
        Example like this:

        ```
        {
            "start_node": "49547ed0-0f86-418e-8dea-a269f7b002f6",
            "end_node": "d9efb3d3-7b5c-49af-83b6-1d39b3f63912",
            "type": "was issued in",
            "properties": {
                "source": "TEXT2KG"
            }
        }
        ```
        Args:
            relationships:

        Returns:

        """
        for relationship in tqdm(relationships, desc="Loading Relationships"):
            start_node = relationship["start_node"]
            end_node = relationship["end_node"]
            relationship_type = relationship["type"]
            properties = relationship.get("properties", {})
            properties_query = ", ".join(
                [f"{key}: ${key}" for key in properties.keys()]
            )
            relationship_query = f"""
            MATCH (start_node {{uuid: $start_node}}), (end_node {{uuid: $end_node}})
            MERGE (start_node)-[r:{relationship_type}]->(end_node)
            ON CREATE SET r += {{{properties_query}}}
            """

            with self.driver.session() as session:
                session.run(
                    relationship_query,
                    start_node=start_node,
                    end_node=end_node,
                    **properties,
                )

    def load_data(self):
        data = self.load_json_data()
        nodes = data["nodes"]
        relationships = data["relationships"]
        self.load_nodes(nodes)
        self.load_relationships(relationships)
        logger.info("Data loaded successfully to Neo4j")
