import os
from functools import lru_cache
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field, SecretStr
from yaml import safe_load

from Docs2KG.utils.constants import (
    DATA_INPUT_DIR,
    DATA_ONTOLOGY_DIR,
    DATA_OUTPUT_DIR,
    PROJECT_DIR,
)

CONFIG_FILE = os.getenv("CONFIG_FILE", PROJECT_DIR / "config.yml")

logger.info(f"Reading configuration from: {CONFIG_FILE}")


class AgentOpenAIConfig(BaseModel):
    api_key: SecretStr
    api_base: str = Field(default="https://api.openai.com/v1")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    timeout: int = Field(default=30)
    max_retries: int = Field(default=2)


class AgentOLLAMAConfig(BaseModel):
    api_base: str = Field(default="http://localhost:11434")
    timeout: int = Field(default=30)
    max_retries: int = Field(default=2)
    temperature: float = Field(default=0.7)
    context_window: int = Field(default=4096)
    format: str = Field(default="json")
    stream: bool = Field(default=False)


class AgentHuggingFaceConfig(BaseModel):
    api_token: SecretStr
    api_base: str = Field(default="https://api-inference.huggingface.co/models")
    timeout: int = Field(default=30)


class AgentLlamaCppConfig(BaseModel):
    context_length: int = Field(default=4096)
    num_threads: int = Field(default=1)
    gpu_layers: int = Field(default=0)
    max_tokens: int = Field(default=2000)
    top_p: float = Field(default=0.9)
    stop_tokens: list = Field(default=["\n", "\n\n", "\n\n\n"])
    temperature: float = Field(default=0.7)
    model_path: str = Field(default="models/llama-7b.gguf")


class DataConfig(BaseModel):
    input_dir: Path = DATA_INPUT_DIR
    output_dir: Path = DATA_OUTPUT_DIR
    ontology_dir: Path = DATA_ONTOLOGY_DIR


class SemanticKGConfig(BaseModel):
    entity_list: str = Field(default="entity_list.csv")
    relation_list: str = Field(default="relation_list.csv")
    ontology: str = Field(default="ontology.json")
    domain_description: str = Field(default="domain_description.txt")


class Config(BaseModel):
    openai: AgentOpenAIConfig
    ollama: AgentOLLAMAConfig
    huggingface: AgentHuggingFaceConfig
    llamacpp: AgentLlamaCppConfig
    data: DataConfig
    semantic_kg: SemanticKGConfig

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "Config":
        """Load configuration from a YAML file."""
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_path) as f:
            config_dict = safe_load(f)

        return cls(**config_dict)


@lru_cache()
def get_config() -> Config:
    """
    Get the configuration singleton.
    The lru_cache decorator ensures this is only created once and reused.
    """
    try:
        config = Config.from_yaml(CONFIG_FILE)
        logger.info("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# Initialize configuration at startup
PROJECT_CONFIG = get_config()

logger.debug(PROJECT_CONFIG)

# Usage in other files:
# from .config import config
# api_key = config.openai.api_key.get_secret_value()
