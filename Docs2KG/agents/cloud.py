from typing import Any, Dict, Optional

from loguru import logger
from openai import OpenAI

from Docs2KG.agents.base import BaseAgent
from Docs2KG.agents.config import CLOUD_MODEL_CONFIGS


OPENAI_API_KEY = (
    "sk-1234567890abcdef1234567890abcdef"  # Replace with your OpenAI API key
)


class CloudAgent(BaseAgent):
    def __init__(self, name: str, api_key: Optional[str] = None):
        """
        Initialize CloudAgent with model name and optional API key.

        Args:
            name: Name of the model to use (e.g., 'gpt-4')
            api_key: Optional OpenAI API key. If not provided, will look for
                    OPENAI_API_KEY in environment variables or .env file
        """
        super().__init__(name)
        self.model = self._init_model_config()
        self.client = self._init_openai_client()

    def _init_model_config(self) -> Dict[str, Any]:
        """Initialize model configuration from predefined configs"""
        model_name = self.name.lower()
        config = CLOUD_MODEL_CONFIGS.get(model_name, CLOUD_MODEL_CONFIGS["gpt-4o"])
        if not config:
            logger.error(f"No configuration found for model: {model_name}")
            raise ValueError(f"Invalid model name: {model_name}")
        return config

    def _init_openai_client(self) -> OpenAI:
        """
        Initialize OpenAI client with API key from either:
        1. Explicitly passed api_key parameter
        2. Environment variable OPENAI_API_KEY
        3. .env file
        """
        try:
            # Initialize client with config
            client = OpenAI(
                api_key=OPENAI_API_KEY,
                base_url=self.model.get("api_base", "https://api.openai.com/v1"),
                timeout=self.model.get("timeout", 30),
                max_retries=self.model.get("max_retries", 2),
            )

            logger.info(f"Successfully initialized OpenAI client for model {self.name}")
            return client

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def process(self, input_data: Any) -> Any:
        """
        Process input using the OpenAI client.

        Args:
            input_data: The input to be processed by the model

        Returns:
            Dict containing the model response and metadata
        """
        logger.info(f"Using cloud model: {self.model['model']}")
        logger.info(f"Processing with configurations: {self.model}")

        try:
            # Create chat completion with proper error handling
            response = self.client.chat.completions.create(
                model=self.model["model"],
                messages=[{"role": "user", "content": str(input_data)}],
                max_tokens=self.model.get("max_tokens", 4096),
                temperature=self.model.get("temperature", 0.7),
                top_p=self.model.get("top_p", 1.0),
                presence_penalty=self.model.get("presence_penalty", 0),
                frequency_penalty=self.model.get("frequency_penalty", 0),
            )

            return {
                "model": self.model["model"],
                "input": input_data,
                "status": "processed",
                "response": response.choices[0].message.content,
                "usage": response.usage.dict() if response.usage else None,
            }

        except Exception as e:
            logger.error(f"Error processing input with OpenAI: {str(e)}")
            raise
