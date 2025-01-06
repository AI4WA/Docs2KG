from typing import Any

from huggingface_hub import InferenceClient
from loguru import logger

from Docs2KG.agents.base import BaseAgent
from Docs2KG.utils.config import PROJECT_CONFIG


class HuggingFaceAgent(BaseAgent):
    def __init__(self, name: str):
        """
        Initialize HuggingFaceAgent with model name.

        Args:
            name: Name of the model to use (e.g., 'gpt2')
        """
        super().__init__(name)
        self.client = self._init_huggingface_client()

    def _init_huggingface_client(self) -> InferenceClient:
        """
        Initialize HuggingFace client with API token from either:
        1. Environment variable HF_API_TOKEN
        2. .env file
        """
        try:
            # Initialize client with config
            client = InferenceClient(
                model=self.name,
                token=PROJECT_CONFIG.huggingface.api_token.get_secret_value(),
            )

            logger.info(
                f"Successfully initialized HuggingFace client for model {self.name}"
            )
            return client

        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace client: {str(e)}")
            raise

    def process(self, input_data: Any) -> Any:
        """
        Process input using the HuggingFace client.

        Args:
            input_data: The input to be processed by the model

        Returns:
            Dict containing the model response and metadata
        """
        logger.info(f"Processing input with HuggingFace: {input_data}")

        try:
            # Query the model with proper error handling
            response = self.client.text_generation(
                prompt=str(input_data),
                details=True,  # Get detailed response including token counts
                return_full_text=False,  # Only return generated text, not the prompt
            )

            return {
                "model": self.name,
                "input": input_data,
                "status": "processed",
                "response": response.generated_text,
                "usage": {
                    "prompt_tokens": len(str(input_data).split()),
                    "completion_tokens": len(response.generated_text.split()),
                    "total_tokens": len(str(input_data).split())
                    + len(response.generated_text.split()),
                },
            }

        except Exception as e:
            logger.error(f"Error processing input with HuggingFace: {str(e)}")
            raise
