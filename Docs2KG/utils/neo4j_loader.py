import json
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
from neo4j import GraphDatabase, basic_auth

from Docs2KG.utils.config import PROJECT_CONFIG
from Docs2KG.utils.timer import timer


class Neo4jTransformer:
    def __init__(
        self,
        project_id: str,
        uri: str,
        username: str,
        password: str,
        database: Optional[str] = None,
        reset_database: bool = False,
    ):
        """Initialize the transformer with Neo4j connection details"""
        self.project_id = project_id
        self.driver = GraphDatabase.driver(uri, auth=basic_auth(username, password))
        self.database = database
        self.reset_database = reset_database
        self.layout_schema_path = (
            PROJECT_CONFIG.data.output_dir
            / "projects"
            / project_id
            / "layout"
            / "schema.json"
        )
        self.layout_schema = self._load_layout_schema()
        self.header_stack = []  # Track header hierarchy
        self.current_file_id = None
        if self.reset_database:
            with self.driver.session(database=self.database) as session:
                session.run("MATCH (n) DETACH DELETE n")

    def _load_layout_schema(self) -> Dict:
        """Load layout schema from file"""
        with open(self.layout_schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_metadata_kg(self, session):
        """
        Loads a metadata knowledge graph from a JSON file into Neo4j.
        - Creates/merges a :Project node with the given project_id if not existing.
        - Loads all 'nodes' into :Node label. Each node's 'properties' are flattened into separate node properties.
        - Loads all 'relationships' using a :RELATES_TO relationship.
        """

        # 1. Check the metadata_kg file exists.
        metadata_kg_path = (
            PROJECT_CONFIG.data.output_dir
            / "projects"
            / self.project_id
            / "metadata_kg.json"
        )
        if not metadata_kg_path.exists():
            logger.error(f"Metadata knowledge graph not found at {metadata_kg_path}")
            return None

        # first check if the project node exists
        project_query = """
        MATCH (p:Project {id: $project_id})
        RETURN p
        """

        result = session.run(project_query, project_id=self.project_id)
        project_node = result.single()
        if project_node is not None:
            logger.info(f"Project {self.project_id} already exists. Skipping load.")
            return

        # 2. Merge the :Project node to ensure the label is created and the node is present.
        #    If it already exists, we can decide whether to skip or proceed.
        project_merge_query = """
        MERGE (p:Project {id: $project_id})
        ON CREATE SET p.createdAt = timestamp()
        RETURN p
        """
        session.run(project_merge_query, project_id=self.project_id)

        # 3. Load the JSON content
        with open(metadata_kg_path, "r", encoding="utf-8") as f:
            metadata_kg = json.load(f)

        # 4. Insert all nodes
        #    We flatten node["properties"] into the node so that each key in `properties`
        #    is stored as a direct property on the node. If you prefer to store them as a single
        #    JSON string, see the alternative approach commented below.

        with timer(logger, "Loading metadata knowledge graph: Nodes"):
            for node in metadata_kg["nodes"]:
                # node["properties"] must be a dict of {string_key -> scalar_value}
                # so that `SET n += $props` can distribute them as node properties.

                # Example: for {"ANumber":144050}, this becomes n.ANumber = 144050
                node_props = node["properties"] if "properties" in node else {}

                # If you want each node's type to be an actual Neo4j label, you can do:
                #   create_node_cypher = "CREATE (n:" + node["type"] + " {id: $id}) SET n += $props"
                #   but that depends on your domain model.

                # add project_id to node properties
                node_props["project_id"] = self.project_id
                create_node_cypher = (
                    """
                    CREATE (n:"""
                    + node.get("type", "Node")
                    + """{id: $id, type: $type})
                SET n += $props
                """
                )
                session.run(
                    create_node_cypher,
                    id=node["id"],
                    label=node.get("type", "Node"),  # fallback empty string if no type
                    type=node.get("type", ""),  # fallback empty string if no type
                    props=node_props,
                )

        with timer(logger, "Loading metadata knowledge graph: Relationships"):
            for relation in metadata_kg["relationships"]:
                # cypher query to match the id of the start and end nodes
                # and create a relationship between them
                create_relationship_cypher = """
                MATCH (start), (end)
                WHERE start.id = $start_id AND end.id = $end_id
                CREATE (start)-[:RELATES_TO $props]->(end)
                """
                # add project_id to relationship properties
                relation_props = (
                    relation["properties"] if "properties" in relation else {}
                )
                relation_props["project_id"] = self.project_id
                session.run(
                    create_relationship_cypher,
                    start_id=relation["source"],
                    end_id=relation["target"],
                    props=relation_props,
                )

        logger.info(f"Metadata knowledge graph loaded for project {self.project_id}.")
        return True

    def close(self):
        """Close the Neo4j driver"""
        self.driver.close()

    def merge_entities(self):
        """Merge entities with same label and text within the same project"""
        with self.driver.session(database=self.database) as session:
            # First, find duplicate entities (same label, text, and project)
            find_duplicates_query = """
            MATCH (e1)
            WHERE e1.text IS NOT NULL AND e1.method IS NOT NULL  // ensure it's an entity
            WITH e1.text as text, labels(e1)[0] as label, e1.project_id as project_id,
                 collect(e1) as entities, count(*) as count
            WHERE count > 1
            RETURN text, label, project_id, entities
            """

            duplicates = session.run(find_duplicates_query)

            for record in duplicates:

                entities = record["entities"]

                # Keep first entity as primary
                primary_entity = entities[0]
                duplicate_entities = entities[1:]

                # For each duplicate
                for dup_entity in duplicate_entities:
                    # First, redirect all incoming relationships
                    session.run(
                        """
                    MATCH (dup) WHERE elementId(dup) = $dup_id
                    MATCH (primary) WHERE elementId(primary) = $primary_id
                    MATCH (dup)<-[r]-()
                    WITH dup, r, startNode(r) as start_node, primary, properties(r) as props
                    CREATE (start_node)-[new_r:HAS_ENTITY]->(primary)
                    SET new_r = props
                    WITH dup, r
                    DELETE r
                    """,
                        dup_id=dup_entity.element_id,
                        primary_id=primary_entity.element_id,
                    )

                    # Then, redirect all outgoing relationships
                    session.run(
                        """
                    MATCH (dup) WHERE elementId(dup) = $dup_id
                    MATCH (primary) WHERE elementId(primary) = $primary_id
                    MATCH (dup)-[r]->()
                    WITH dup, r, endNode(r) as end_node, primary, properties(r) as props
                    CREATE (primary)-[new_r:RELATES_TO]->(end_node)
                    SET new_r = props
                    WITH dup, r
                    DELETE r
                    """,
                        dup_id=dup_entity.element_id,
                        primary_id=primary_entity.element_id,
                    )

                    # Finally, delete duplicate node
                    session.run(
                        """
                    MATCH (dup) WHERE elementId(dup) = $dup_id
                    DELETE dup
                    """,
                        dup_id=dup_entity.element_id,
                    )

            # Create uniqueness constraint if it doesn't exist
            try:
                session.run(
                    """
                CREATE CONSTRAINT unique_entity IF NOT EXISTS
                FOR (e:Entity)
                REQUIRE (e.text, e.label, e.project_id) IS UNIQUE
                """
                )
            except Exception as e:
                # Handle older Neo4j versions or other constraint errors
                print(f"Warning: Could not create constraint - {str(e)}")

    def transform_and_load(self, input_path: Path):
        """Transform and load data into Neo4j"""
        if "layout" not in str(input_path):
            logger.warning("Input file is not a layout knowledge graph")
            return
        layout_json = json.load(open(input_path, "r", encoding="utf-8"))

        with self.driver.session(database=self.database) as session:
            # Load metadata knowledge graph
            self.load_metadata_kg(session)

            # Create file node with unique ID
            self.current_file_id = f"{self.project_id}_{layout_json['filename']}"
            file_props = {
                "id": self.current_file_id,
                "filename": layout_json["filename"],
                "project_id": self.project_id,
            }

            session.run(
                """
                CREATE (f:File $props)
                """,
                props=file_props,
            )

            # Reset state
            self.header_stack = []

            # Process layout structure
            self._create_layout(session, layout=layout_json["data"])

            # Process entities and relations
            for item in layout_json["data"]:
                self._process_entities(session, item)
                self._process_relations(session, item)

            # Merge duplicate entities after all data is loaded
            self.merge_entities()

    def _find_parent_node(
        self, session, current_item: Dict, previous_items: List[Dict]
    ) -> Optional[str]:
        """Find the appropriate parent node ID based on document structure rules"""
        current_label = current_item["label"]

        # If it's a header, handle header hierarchy
        if current_label.startswith("H"):
            current_level = int(current_label[1])

            # Update header stack
            while (
                self.header_stack and int(self.header_stack[-1][0][1]) >= current_level
            ):
                self.header_stack.pop()

            if not self.header_stack:
                return None  # Connect to File node

            return self.header_stack[-1][1]  # Return last valid header's ID

        # For non-header nodes, check schema rules
        if previous_items:
            prev_item = previous_items[-1]
            prev_label = prev_item["label"]

            # If previous label can contain current label according to schema
            if (
                prev_label in self.layout_schema
                and current_label in self.layout_schema[prev_label]
            ):
                return prev_item["id"]

            # If there's a header context
            if self.header_stack:
                return self.header_stack[-1][1]

        return None  # Default to connecting to File node

    def _create_layout(self, session, layout: List[Dict]):
        """Create layout structure with proper hierarchical relationships"""
        processed_items = []

        for idx, item in enumerate(layout):
            item_props = {
                "id": item["id"],
                "text": item.get("text", ""),
                "sequence": idx,
                "project_id": self.project_id,
            }

            label = self.sanitize_label(item.get("label", "Item"))

            # Find parent node
            parent_id = self._find_parent_node(session, item, processed_items)

            if parent_id:
                # Create node with relationship to parent
                query = f"""
                MATCH (p) WHERE p.id = $parent_id
                CREATE (p)-[:CONTAINS]->(n:{label} $props)
                RETURN n
                """
                session.run(query, parent_id=parent_id, props=item_props)
            else:
                # Create node with relationship to file
                query = f"""
                MATCH (f:File {{id: $file_id}})
                CREATE (f)-[:CONTAINS]->(n:{label} $props)
                RETURN n
                """
                session.run(query, file_id=self.current_file_id, props=item_props)

            # Update header stack if needed
            if label.startswith("H"):
                self.header_stack.append((label, item["id"]))

            # Add to processed items
            processed_items.append(item)

            # Create NEXT relationship with previous node at same level
            if processed_items and len(processed_items) > 1:
                prev_item = processed_items[-2]
                if prev_item["label"] == item["label"]:
                    session.run(
                        """
                        MATCH (p), (n)
                        WHERE p.id = $prev_id AND n.id = $curr_id
                        CREATE (p)-[:NEXT]->(n)
                        """,
                        prev_id=prev_item["id"],
                        curr_id=item["id"],
                    )

    def _process_entities(self, session, item: Dict):
        """Process entities for an item"""
        for entity in item.get("entities", []):
            entity_props = {
                "id": entity.get("id", ""),
                "text": entity.get("text", ""),
                "confidence": entity.get("confidence", 0.0),
                "start": entity.get("start", 0),
                "end": entity.get("end", 0),
                "method": entity.get("method", ""),
                "project_id": self.project_id,
            }

            entity_label = self.sanitize_label(entity.get("label", "Entity"))

            session.run(
                f"""
                MATCH (p) WHERE p.id = $item_id
                CREATE (p)-[:HAS_ENTITY]->(e:{entity_label} $props)
                """,
                item_id=item["id"],
                props=entity_props,
            )

    def _process_relations(self, session, item: Dict):
        """Process relations for an item"""
        for relation in item.get("relations", []):
            relation_props = {
                "type": relation.get("type", "RELATES_TO"),
                "confidence": relation.get("confidence", 0.0),
                "project_id": self.project_id,
            }

            if "source_id" in relation and "target_id" in relation:
                session.run(
                    """
                    MATCH (s), (t)
                    WHERE s.id = $source_id AND t.id = $target_id
                    CREATE (s)-[r:RELATES_TO $props]->(t)
                    """,
                    source_id=relation["source_id"],
                    target_id=relation["target_id"],
                    props=relation_props,
                )

    @staticmethod
    def sanitize_label(label: str) -> str:
        """
        Sanitize label for Neo4j:
        - Replaces spaces and hyphens with underscores
        - Converts to uppercase
        - Moves any leading numbers to the end of the label
        """
        # First sanitize special characters
        sanitized = label.replace(" ", "_").replace("-", "_").upper()

        # If label starts with a number, move leading numbers to end
        if sanitized and sanitized[0].isdigit():
            leading_nums = ""
            i = 0
            while i < len(sanitized) and (
                sanitized[i].isdigit() or sanitized[i] == "_"
            ):
                leading_nums += sanitized[i]
                i += 1
            return f"{sanitized[i:]}{leading_nums}" if i < len(sanitized) else sanitized

        return sanitized

    def get_document_structure(self, file_id: str):
        """Get the document structure as a tree"""
        with self.driver.session(database=self.database) as session:
            query = """
            MATCH path = (f:File {id: $file_id})-[r:CONTAINS|NEXT*]->(n)
            RETURN path
            ORDER BY n.sequence
            """
            results = session.run(query, file_id=file_id)
            return [record["path"] for record in results]

    def export(self):
        """Export the Neo4j database to a JSON file that can be reimported later

        Returns a JSON structure containing nodes and relationships with their properties,
        labels, and types preserved.
        """
        with self.driver.session(database=self.database) as session:
            # Get all nodes with their labels and properties
            nodes_query = """
            MATCH (n)
            RETURN collect({
                id: id(n),
                labels: labels(n),
                properties: properties(n)
            }) as nodes
            """

            # Get all relationships with their types and properties
            rels_query = """
            MATCH ()-[r]->()
            RETURN collect({
                id: id(r),
                type: type(r),
                properties: properties(r),
                startNode: id(startNode(r)),
                endNode: id(endNode(r))
            }) as relationships
            """

            nodes = session.run(nodes_query).single()["nodes"]
            relationships = session.run(rels_query).single()["relationships"]

            export_data = {"nodes": nodes, "relationships": relationships}

            # Write to file
            neo4j_export = (
                PROJECT_CONFIG.data.output_dir
                / "projects"
                / self.project_id
                / "neo4j_export.json"
            )
            with open(neo4j_export, "w") as f:
                json.dump(export_data, f, indent=2)

        logger.info("Exported Neo4j database to neo4j_export.json")
        return export_data

    def import_from_json(self, filepath):
        """Import the Neo4j database from a previously exported JSON file"""
        with open(filepath, "r") as f:
            json_data = json.load(f)

        with self.driver.session(database=self.database) as session:
            # First create all nodes with unique identifiers
            node_mapping = {}  # To store mapping between old and new elementIds

            for node in json_data["nodes"]:
                labels = ":".join(node["labels"])
                properties = dict(node["properties"])

                # Create node and return its elementId
                create_node_query = f"""
                CREATE (n:{labels})
                SET n = $properties
                RETURN elementId(n) as new_id
                """
                result = session.run(create_node_query, properties=properties)
                new_id = result.single()["new_id"]
                node_mapping[node["id"]] = new_id

            # Then create all relationships using the new elementIds
            for rel in json_data["relationships"]:
                rel_type = rel["type"]
                properties = dict(rel["properties"])
                start_id = node_mapping[rel["startNode"]]
                end_id = node_mapping[rel["endNode"]]

                create_rel_query = f"""
                MATCH (start), (end)
                WHERE elementId(start) = $start_id AND elementId(end) = $end_id
                CREATE (start)-[r:{rel_type}]->(end)
                SET r = $properties
                """
                session.run(
                    create_rel_query,
                    start_id=start_id,
                    end_id=end_id,
                    properties=properties,
                )

        logger.info(f"Imported Neo4j database from {filepath}")


# Example usage:
if __name__ == "__main__":
    example_project_id = "default"
    example_json = (
        PROJECT_CONFIG.data.output_dir
        / "projects"
        / example_project_id
        / "layout"
        / "2405.14831v1.json"
    )
    with open(example_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Connection details
    NEO4J_URI = "neo4j://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "testpassword"

    # Load data
    with open(example_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Initialize transformer and load data
    transformer = Neo4jTransformer(
        project_id=example_project_id,
        uri=NEO4J_URI,
        username=NEO4J_USER,
        password=NEO4J_PASSWORD,
        reset_database=True,
    )

    # try:
    #     # Transform and load data
    #     transformer.transform_and_load(data)
    #
    #     # Export Neo4j database
    #     transformer.export()
    # finally:
    #     transformer.close()
    #
    try:
        # Import Neo4j database
        transformer.import_from_json(
            PROJECT_CONFIG.data.output_dir
            / "projects"
            / example_project_id
            / "neo4j_export.json"
        )
    finally:
        transformer.close()
