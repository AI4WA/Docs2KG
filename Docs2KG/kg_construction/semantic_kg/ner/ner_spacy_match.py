from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import pandas as pd
import spacy
from loguru import logger
from spacy.matcher import Matcher
from tqdm import tqdm

from Docs2KG.agents.func.ner_llm_judge import NERLLMJudge
from Docs2KG.kg_construction.semantic_kg.base import SemanticKGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG
from Docs2KG.utils.timer import timer


class NERSpacyMatcher(SemanticKGConstructionBase):
    """
    To get this working, need to run: python -m spacy download en_core_web_sm first

    """

    def __init__(
        self,
        project_id: str,
        agent_name: str = "phi3.5",
        agent_type: str = "ollama",
    ):
        super().__init__(project_id)
        # Load SpaCy model (use a smaller model for speed)
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        self.entity_dict = {}
        self.load_entity_list()
        self.llm_judgement_agent = NERLLMJudge(agent_name, agent_type)

    def load_entity_list(self):
        try:
            entity_list_path = Path(PROJECT_CONFIG.semantic_kg.entity_list)
            if not entity_list_path.exists():
                raise FileNotFoundError(f"Entity list not found at {entity_list_path}")
            with timer(logger, "Loading entity list"):
                df = pd.read_csv(entity_list_path, sep=r",(?=[^,]*$)", engine="python")
            self.entity_dict = dict(zip(df["entity"], df["entity_type"]))
            self._initialize_patterns()

        except Exception as e:
            logger.error(f"Error loading entity list: {e}")
            return

    def _initialize_patterns(self):
        """
        Convert entity dictionary to SpaCy patterns
        Handles both single-word and multi-word entities
        """
        patterns = []

        for entity_text, entity_type in self.entity_dict.items():
            # Convert entity text to lowercase
            entity_lower = entity_text.lower()

            # Split entity text into tokens
            tokens = entity_lower.split()

            # Create pattern for exact matching
            pattern = [{"LOWER": token} for token in tokens]

            # Add pattern to matcher with unique ID
            pattern_id = f"{entity_type}_{hash(entity_lower)}"
            self.matcher.add(pattern_id, [pattern])

            # Store mapping of pattern_id to original entity text and type
            patterns.append(
                {
                    "id": pattern_id,
                    "text": entity_text,
                    "type": entity_type,
                    "pattern": pattern,
                }
            )

        self.patterns = patterns

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Given the text, find the case-insensitive match of the entities in the entity dict.
        Uses SpaCy Matcher to find the entities in the text first.

        Args:
            text (str): The input text to search for entities

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
        if not text or not self.entity_dict:
            return []
        text = text.lower()
        # Process text with SpaCy
        doc = self.nlp(text)

        # Find matches using the matcher
        matches = self.matcher(doc)

        # Convert matches to our format
        results = []
        for match_id, start, end in matches:
            # Get the matched span
            span = doc[start:end]

            # Get the original text from the span
            matched_text = span.text

            # Find corresponding pattern info
            pattern_id = self.nlp.vocab.strings[match_id]
            entity_info = next(
                (p for p in self.patterns if p["id"] == pattern_id), None
            )

            if entity_info:
                # Create match entry
                if not self._validate_match(doc, start, end):
                    continue

                is_correct = self.llm_judgement_agent.judge(
                    ner=matched_text, ner_type=entity_info["type"], text=text
                )
                if not is_correct:
                    continue

                match = {
                    "id": f"ner-spacy-{hash(matched_text + str(start) + str(end))}-{str(uuid4())}",
                    "start": span.start_char,
                    "end": span.end_char,
                    "text": matched_text,
                    "label": entity_info["type"],
                    "confidence": (
                        0.95
                        if matched_text.lower() == entity_info["text"].lower()
                        else 0.9
                    ),
                    "method": self.__class__.__name__,
                }
                results.append(match)

        # Sort results by start position
        results.sort(key=lambda x: x["start"])

        logger.info(f"Extracted entities: {results} for text: {text}")
        return results

    @staticmethod
    def _validate_match(doc, start, end):
        """
        Validate if a match is at proper word boundaries

        Args:
            doc: SpaCy Doc object
            start: Start token index
            end: End token index

        Returns:
            bool: Whether the match is valid
        """

        # Check if the span is at token boundaries
        if start > 0 and doc[start - 1].is_alpha:
            return False
        if end < len(doc) and doc[end].is_alpha:
            return False

        return True

    def construct_kg(self, input_data: List[Path]) -> None:
        """
        Construct a semantic knowledge graph from input data.

        Args:
            input_data: Input data to construct the knowledge graph
        """
        # Process each document
        for doc in tqdm(input_data, desc="Processing documents"):
            # Extract entities from the document text
            if not doc.exists():
                logger.error(f"Document not found at {doc}")
                continue
            logger.info(f"Processing document: {doc}")
            layout_kg = self.load_layout_kg(doc)
            if "data" not in layout_kg:
                logger.error(f"Document data not found in {doc}")
                continue
            for item in layout_kg["data"]:
                if "text" not in item:
                    logger.error(f"Text not found in document item: {item}")
                    continue
                text = item["text"]
                entities = self.extract_entities(text)
                # expand the item entities list with the extracted entities
                item["entities"].extend(entities)
                # then remove duplicated entities based on start and end positions, text and label
                item["entities"] = self.unique_entities(item["entities"])

            self.update_layout_kg(doc, layout_kg)


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
    entity_extractor = NERSpacyMatcher(example_project_id)
    entity_extractor.construct_kg([example_json])
