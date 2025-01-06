import json
from pathlib import Path
from typing import Optional

from loguru import logger

from Docs2KG.agents.manager import AgentManager
from Docs2KG.kg_construction.semantic_kg.base import SemanticKGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG
from Docs2KG.utils.models import Ontology
from Docs2KG.utils.timer import timer


class EntityTypesLLMGenerator(SemanticKGConstructionBase):
    """
    It will query the
    - project description
    - content of the pdf (total text)
    - current entity type list

    And then ask the LLM to generate the entity types.

    Also, we will combine generated entity types with the current entity type list.
    And update the entity type list within the folder

    """

    def __init__(
        self, project_id: str, agent_name="phi3.5", agent_type="ollama", **kwargs
    ):
        super().__init__(project_id)
        self.ontology_agent = AgentManager(agent_name, agent_type, **kwargs)
        # first load project description
        self.project_description = self.load_project_description()
        self.load_entity_type()

    @staticmethod
    def load_project_description():
        project_description_path = Path(PROJECT_CONFIG.semantic_kg.domain_description)
        if not project_description_path.exists():
            raise FileNotFoundError(
                f"Project description not found at {project_description_path}"
            )
        with open(project_description_path, "r") as file:
            project_description = file.read()
        return project_description

    def generate_entity_types(
        self,
        content: Optional[str] = None,
    ):
        prompt = f"""You are a expert to generate entity types based on the following project description:
                    '{self.project_description}'
                    and the content of the pdf:
                    '{content}'

                    The current entity types are:
                    {self.entity_type_list}

                    Please generate some new related entity types based on the information above
                    **mainly based on the content of pdf**
                    Do not generate repeated entity types.

                    Generated entity type should be short, concise, representative and concise.

                    Return in JSON format with key entity_types,
                    and value as a list of entity types which will be a string of the entity type, separated by comma.

                    If the current entity types already cover most of the entities, you can return an empty list.
                    """

        response = self.ontology_agent.process_input(prompt, reset_session=True)
        res_json_str = response["response"]
        logger.debug(f"LLM response: {res_json_str}")
        new_entity_types = self.extract_entity_types(res_json_str)
        logger.critical(f"New entity types: {new_entity_types}")
        return new_entity_types

    @staticmethod
    def extract_entity_types(res_json_str):
        try:
            res_json_str = res_json_str.strip()
            res_json = json.loads(res_json_str)
            entity_types_list_str = res_json.get("entity_types", "")
            if isinstance(entity_types_list_str, list):
                entity_types = entity_types_list_str
            else:
                entity_types_list_str = entity_types_list_str.strip()
                entity_types = entity_types_list_str.split(",")
            entity_types = [entity_type.strip() for entity_type in entity_types]
            return entity_types
        except Exception as e:
            logger.error(f"Failed to extract entity types from response: {str(e)}")
            return None

    def construct_ontology(self):
        new_entity_types = self.generate_entity_types()
        logger.critical(f"New entity types: {new_entity_types}")
        if new_entity_types:
            self.update_ontology(new_entity_types)

    @staticmethod
    def update_ontology(new_entity_types):
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
            ontology_entity_types = ontology.entity_types

        new_entity_types = list(set(new_entity_types) | set(ontology_entity_types))
        ontology.entity_types = new_entity_types
        json_str = ontology.model_dump_json()
        with open(ontology_json_path, "w") as f:
            f.write(json_str)


if __name__ == "__main__":
    example_project_id = "wamex"
    entity_types_llm_generator = EntityTypesLLMGenerator(example_project_id)
    entity_types_llm_generator.construct_ontology()
