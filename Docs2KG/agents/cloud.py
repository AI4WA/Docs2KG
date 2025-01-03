from typing import Any

from loguru import logger
from openai import OpenAI

from Docs2KG.agents.base import BaseAgent
from Docs2KG.utils.config import PROJECT_CONFIG


class CloudAgent(BaseAgent):
    def __init__(self, name: str):
        """
        Initialize CloudAgent with model name and optional API key.

        Args:
            name: Name of the model to use (e.g., 'gpt-4')
        """
        super().__init__(name)
        self.client = self._init_openai_client()

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
                api_key=PROJECT_CONFIG.openai.api_key.get_secret_value(),
                base_url=PROJECT_CONFIG.openai.api_base,
                timeout=PROJECT_CONFIG.openai.timeout,
                max_retries=PROJECT_CONFIG.openai.max_retries,
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
        logger.info(f"Processing input with OpenAI: {input_data}")

        try:
            # Create chat completion with proper error handling
            response = self.client.chat.completions.create(
                model=self.name,
                messages=[{"role": "user", "content": str(input_data)}],
                max_tokens=PROJECT_CONFIG.openai.max_tokens,
                temperature=PROJECT_CONFIG.openai.temperature,
            )

            return {
                "model": self.name,
                "input": input_data,
                "status": "processed",
                "response": response.choices[0].message.content,
                "usage": response.usage.dict() if response.usage else None,
            }

        except Exception as e:
            logger.error(f"Error processing input with OpenAI: {str(e)}")
            raise
