import json
import re
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from Docs2KG.agents.manager import AgentManager
from Docs2KG.kg_construction.semantic_kg.base import SemanticKGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG


class NEROntoLLMPromptExtractor(SemanticKGConstructionBase):
    """
    Extract named entities using LLM and Entity Types from ontology.json
    """

    def __init__(
        self,
        project_id: str,
        agent_name="phi3.5",
        agent_type="ollama",
        **kwargs,
    ):
        """
        Initialize LLM NER Extractor with ontology-based entity types

        Args:
            project_id: Project ID
            agent_name: Name of the agent to use
            agent_type: Type of agent (ollama, cloud, etc.)
        """
        super().__init__(
            project_id=project_id,
        )

        self.llm_ner_extract_agent = AgentManager(agent_name, agent_type, **kwargs)
        self.entity_type_list = []
        self.load_entity_types_from_ontology()

    def load_entity_types_from_ontology(self):
        """
        Load entity types from the ontology.json file
        """
        try:
            ontology_path = Path("data/ontology/ontology.json")
            if not ontology_path.exists():
                logger.error(f"Ontology file not found at {ontology_path}")
                return

            with open(ontology_path, "r") as f:
                ontology_data = json.load(f)

            if "entity_types" in ontology_data:
                # Filter out entity types that are all uppercase (likely metadata or system types)
                self.entity_type_list = [
                    entity_type
                    for entity_type in ontology_data["entity_types"]
                    if not (entity_type.isupper() or "_" in entity_type)
                ]
                logger.info(f"Loaded entity types: {self.entity_type_list}")
                logger.info(
                    f"Loaded {len(self.entity_type_list)} entity types from ontology"
                )
            else:
                logger.error("No entity_types found in ontology file")
        except Exception as e:
            logger.error(f"Failed to load entity types from ontology: {str(e)}")
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

            The text is:

            {chunk.lower()}

            It should be one of the following entity types from the geological ontology:
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
            If it is not an entity, return an empty array.
            """

            try:
                # Process chunk
                res = self.llm_ner_extract_agent.process_input(
                    chunk_prompt, reset_session=True
                )
                res_json_str = res["response"].strip()
                logger.info(f"Raw response: {res_json_str}")

                # Clean JSON string if it's wrapped in markdown code blocks
                res_json_str = self.clean_json_response(res_json_str)

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
                f"ner-onto-{hash(entity['text'] + str(entity['start']) + str(entity['end']) + entity['label'])}"
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
                # extend the extracted entities to the layout knowledge graph
                item["entities"].extend(entities)
                # remove duplicated entities based on start and end positions, text and label
                item["entities"] = self.unique_entities(item["entities"])

            self.update_layout_kg(layout_kg_path, layout_kg)

    def clean_json_response(self, text):
        """
        Clean the JSON response from LLM that might be wrapped in code blocks

        Args:
            text: The raw text response from LLM

        Returns:
            str: Cleaned JSON string
        """
        # If the response contains markdown code blocks with json
        if "```json" in text:
            # Extract content between ```json and ```
            pattern = r"```json\s*([\s\S]*?)\s*```"
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()

        # If the response contains generic markdown code blocks
        elif "```" in text:
            # Extract content between ``` and ```
            pattern = r"```\s*([\s\S]*?)\s*```"
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()

        return text


if __name__ == "__main__":
    # Test entity extraction
    example_project_id = "wamex"
    example_json = (
        PROJECT_CONFIG.data.output_dir
        / "projects"
        / example_project_id
        / "layout"
        / "a65054_a065054_c321_1993_fwp_annual_report_2001_2002_14067246__OCR__docs2kg_2025-05-21T04-06-28-655Z.json"
    )
    # ner_extractor = NEROntoLLMPromptExtractor(
    #     project_id=example_project_id,
    #     agent_name="phi3.5",
    #     agent_type="ollama",
    # )
    ner_extractor = NEROntoLLMPromptExtractor(
        project_id=example_project_id,
        agent_name="gpt-4o",
        agent_type="cloud",
    )
    ner_extractor.construct_kg([example_json])
