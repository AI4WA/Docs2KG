import json
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from Docs2KG.kg_construction.base import KGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG
from Docs2KG.utils.models import Ontology
from Docs2KG.utils.timer import timer


class SemanticKGConstructionBase(KGConstructionBase):
    """
    Starting from the layout json, we will have several different ways to extract entities and relationships from the documents

    The task will typically into two parts:
    - Named Entity Recognition: extract entities from the text
        - input can be: entity list, ontology, or just description
    - Relationship Extraction: extract relationships between entities

    Input will be an array of layout json files, output will be another json with entities and relationships extracted
    """

    def __init__(self, project_id: str):
        super().__init__(project_id)

    @staticmethod
    def load_layout_kg(layout_kg_path: Path) -> dict:
        """
        Load the layout knowledge graph from a file.

        Args:
            layout_kg_path: Path to the layout knowledge graph file

        Returns:
            dict: Layout knowledge graph
        """
        if not layout_kg_path.exists():
            raise FileNotFoundError(
                f"Layout knowledge graph not found at {layout_kg_path}"
            )
        with open(layout_kg_path, "r") as file:
            layout_kg = json.load(file)
        return layout_kg

    def load_entity_type(self):
        # read from the entity list and ontology json
        # update ontology json based on the entity list if needed
        try:
            entity_list_path = Path(PROJECT_CONFIG.semantic_kg.entity_list)
            if not entity_list_path.exists():
                raise FileNotFoundError(f"Entity list not found at {entity_list_path}")
            with timer(logger, "Loading entity list"):
                df = pd.read_csv(entity_list_path, sep=r",(?=[^,]*$)", engine="python")
            # get all entity types
            entity_type_list = df["entity_type"].unique()
            # read from ontology json
            ontology_json_path = Path(PROJECT_CONFIG.semantic_kg.ontology)
            if not ontology_json_path.exists():
                logger.warning(f"Ontology json not found at {ontology_json_path}")
                ontology_entity_types = []
            else:
                with timer(logger, "Loading ontology json"):
                    with open(ontology_json_path, "r") as f:
                        ontology_json = json.load(f)
                logger.info(f"Ontology json: {ontology_json}")
                ontology = Ontology(**ontology_json)
                # get all entity types from ontology
                ontology_entity_types = ontology.entity_types

            # combine the entity types from entity list and ontology
            self.entity_type_list = list(
                set(entity_type_list) | set(ontology_entity_types)
            )
            # update ontology json if needed
            if len(self.entity_type_list) > len(ontology_entity_types):
                ontology.entity_types = self.entity_type_list
                json_str = ontology.model_dump_json()
                with open(ontology_json_path, "w") as f:
                    f.write(json_str)
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_layout_kg(layout_kg_path: Path, layout_kg: dict) -> None:
        """
        Update the layout knowledge graph in a file.

        Args:
            layout_kg_path: Path to the layout knowledge graph file
            layout_kg: Layout knowledge graph to update
        """
        with open(layout_kg_path, "w") as file:
            json.dump(layout_kg, file, indent=2)

    def construct_kg(self, input_data: Any) -> None:
        """
        Construct a semantic knowledge graph from input data.

        Args:
            input_data: Input data to construct the knowledge graph
        """
        pass

    @staticmethod
    def unique_entities(entities):
        unique_entities = []
        seen_entities = set()
        for entity in entities:
            key = (
                entity["start"],
                entity["end"],
                entity["text"],
                entity["label"],
            )
            if key not in seen_entities:
                unique_entities.append(entity)
                seen_entities.add(key)
        return unique_entities
