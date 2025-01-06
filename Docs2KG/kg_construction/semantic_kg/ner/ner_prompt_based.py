import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from loguru import logger

from Docs2KG.agents.manager import AgentManager
from Docs2KG.kg_construction.semantic_kg.base import SemanticKGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG
from Docs2KG.utils.models import Ontology
from Docs2KG.utils.timer import timer


class NERLLMExtractor(SemanticKGConstructionBase):
    """
    Extract named entities using LLM and Entity Type List
    """

    def __init__(
        self,
        project_id: str,
        agent_name="phi3.5",
        agent_type="ollama",
        **kwargs,
    ):
        """
        Initialize LLM NER Extractor

        Args:
            llm_entity_type_agent: Whether to use LLM for entity type judgement
        """
        super().__init__(
            project_id=project_id,
        )

        self.llm_ner_extract_agent = AgentManager(agent_name, agent_type, **kwargs)
        self.entity_type_list = []
        self.load_entity_type()

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

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from the given text, handling long texts by splitting into chunks

        Args:
            text: Text to extract entities from

        Returns:
            list: List of dictionaries containing entity information with format:
            {
                "id": str,          # Unique identifier for the entity
                "end": int,         # End position in text
                "start": int,       # Start position in text
                "text": str,        # Matched text
                "label": str,       # Entity type/label
                "confidence": float # Confidence score
            }
        """
        if not text or (len(self.entity_type_list) == 0):
            return []

        # Split text into chunks, preserving the periods
        text_chunks = [
            chunk.strip() + "." for chunk in text.split(".") if chunk.strip()
        ]

        # Process each chunk while tracking overall character position
        all_entities = []
        current_position = 0

        for chunk in text_chunks:
            # Create prompt for current chunk
            chunk_prompt = f"""
            Extract entities from the given text:
            {chunk.lower()}

            It should be one of the following entity types:
            {", ".join(self.entity_type_list)}

            Please output a list of entities in the following format via JSON:
            [
                    {{
                        "text": "entity text",
                        "label": "entity type",
                        "confidence": 1.0
                    }},
                    ...
                ]
            
            entity text is the matched text
            entity type is the label of the entity
            confidence is the confidence score of the entity, it should be within [0.0, 1.0]
            You should return it as an array of JSON objects.
            """

            try:
                # Process chunk
                res = self.llm_ner_extract_agent.process_input(
                    chunk_prompt, reset_session=True
                )
                res_json_str = res["response"].strip()
                # logger.info(f"LLM response for chunk: {res_json_str}")

                entities_json = json.loads(res_json_str)
                # if the json is a dict, convert it to a list
                if isinstance(entities_json, dict):
                    entities_json = [entities_json]

                # Verify entities for this chunk
                verified_chunk_entities = self.verify_output_entities(
                    chunk.lower(), entities_json
                )

                logger.info(
                    f"Verified entities for chunk: {len(verified_chunk_entities)}. \n{verified_chunk_entities}"
                )
                # Adjust start and end positions based on current position in overall text
                for entity in verified_chunk_entities:
                    entity["start"] += current_position
                    entity["end"] += current_position
                    entity["method"] = self.__class__.__name__

                all_entities.extend(verified_chunk_entities)

            except Exception as e:
                logger.error(f"Failed to extract entities from chunk: {str(e)}")
                logger.exception(e)
                continue

            # Update current position for next chunk
            current_position += len(chunk)

        logger.critical(
            f"All extracted and verified entities: {len(all_entities)}. \n{all_entities}"
        )
        return all_entities

    def verify_output_entities(
        self, text, entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Verify the extracted entities, the start and end indices is correct

        Args:
            text: Text to extract entities from
            entities: List of extracted entities

        Returns:
            list: List of verified entities
        """
        verified_entities = []
        for entity in entities:
            if entity["label"] not in self.entity_type_list:
                logger.info(
                    f"Dropping entity: {entity} for entity type: {entity['label']}"
                )
                logger.warning(f"Entity type {entity['label']} not in entity type list")
                continue
            entity["start"], entity["end"] = self.locate_text_start_end(text, entity)
            if entity["start"] is None or entity["end"] is None:
                logger.error(f"Failed to locate entity: {entity}")
                continue
            entity["start"], entity["end"] = int(entity["start"]), int(entity["end"])
            # add a unique id for the entity
            entity["id"] = (
                f"ner-llm-{hash(entity['text'] + str(entity['start']) + str(entity['end']) + entity['label'])}"
            )
            verified_entities.append(entity)
        return verified_entities

    @staticmethod
    def verify_entity_position(start, end, text, entity):
        """
        Verify the entity position in the text

        Args:
            start: Start index of the entity
            end: End index of the entity
            text: Text to extract entities from
            entity: Extracted entity

        Returns:
            bool: True if the entity position is correct, False otherwise
        """
        try:
            return text[start:end] == entity["text"]
        except Exception as e:
            logger.error(f"Failed to verify entity position: {str(e)}")
            return False

    @staticmethod
    def locate_text_start_end(text, entity):
        """
        Locate the start and end index of the entity in the text

        Args:
            text: Text to extract entities from
            entity: Extracted entity

        Returns:
            tuple: Start and end index of the entity
        """
        try:
            start = text.find(entity["text"])
            # if start == -1, which means the entity is not found in the text
            if start == -1:
                return None, None
            end = start + len(entity["text"])
            return start, end
        except Exception as e:
            logger.error(f"Failed to locate entity in text: {str(e)}")
            return None, None

    def construct_kg(self, input_data: List[Path]) -> None:
        """
        Construct a semantic knowledge graph from input data.

        Args:
            input_data: Input data to construct the knowledge graph
        """
        logger.info(
            f"Extracting entities from {len(input_data)} layout knowledge graphs"
        )
        for layout_kg_path in input_data:
            if not layout_kg_path.exists():
                logger.error(f"Layout knowledge graph not found at {layout_kg_path}")
                continue
            layout_kg = self.load_layout_kg(layout_kg_path)

            if "data" not in layout_kg:
                logger.error(f"Document data not found in {layout_kg_path}")
                continue

            for item in layout_kg["data"]:
                if "text" not in item:
                    logger.error(f"Text not found in document item: {item}")
                    continue
                text = item["text"]
                entities = self.extract_entities(text)
                item["entities"] = entities

            self.update_layout_kg(layout_kg_path, layout_kg)


if __name__ == "__main__":
    # Test entity extraction
    example_project_id = "wamex"
    example_json = (
        PROJECT_CONFIG.data.output_dir
        / "projects"
        / example_project_id
        / "layout"
        / "gsdRec_2024_08.json"
    )
    # ner_extractor = NERLLMExtractor(
    #     project_id=example_project_id,
    #     agent_name="gpt-4o",
    #     agent_type="cloud",
    # )
    ner_extractor = NERLLMExtractor(
        project_id=example_project_id,
        agent_name="phi3.5",
        agent_type="ollama",
    )
    ner_extractor.construct_kg([example_json])
