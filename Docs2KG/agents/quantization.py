from typing import Any

from llama_cpp import Llama
from loguru import logger

from Docs2KG.agents.base import BaseAgent
from Docs2KG.utils.config import PROJECT_CONFIG


class QuantizationAgent(BaseAgent):
    def __init__(self, name: str):
        """
        Initialize QuantizationAgent with model name.

        Args:
            name: Path to the quantized model file (e.g., 'models/llama-7b-q4.gguf')
        """
        super().__init__(name)
        self.client = self._init_llama_client()

    def _init_llama_client(self) -> Llama:
        """
        Initialize llama.cpp client with the quantized model.
        """
        try:
            # Initialize client with config
            client = Llama(
                model_path=self.name or PROJECT_CONFIG.llamacpp.model_path,
                n_ctx=PROJECT_CONFIG.llamacpp.context_length,
                n_threads=PROJECT_CONFIG.llamacpp.num_threads,
                n_gpu_layers=PROJECT_CONFIG.llamacpp.gpu_layers,
            )

            logger.info(
                f"Successfully initialized llamacpp.cpp client for model {self.name}"
            )
            return client

        except Exception as e:
            logger.error(f"Failed to initialize llamacpp.cpp client: {str(e)}")
            raise

    def process(self, input_data: Any) -> Any:
        """
        Process input using the llamacpp.cpp client.

        Args:
            input_data: The input to be processed by the model

        Returns:
            Dict containing the model response and metadata
        """
        logger.info(f"Processing input with llamacpp.cpp: {input_data}")

        try:
            # Create completion with proper error handling
            response = self.client.create_completion(
                prompt=str(input_data),
                max_tokens=PROJECT_CONFIG.llamacpp.max_tokens,
                temperature=PROJECT_CONFIG.llamacpp.temperature,
                top_p=PROJECT_CONFIG.llamacpp.top_p,
                stop=PROJECT_CONFIG.llamacpp.stop_tokens,
                echo=False,  # Don't include prompt in the response
            )

            # Extract completion tokens used from response metadata
            completion_tokens = len(response["choices"][0]["text"].split())
            prompt_tokens = len(str(input_data).split())

            return {
                "model": self.name,
                "input": input_data,
                "status": "processed",
                "response": response["choices"][0]["text"],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
            }

        except Exception as e:
            logger.error(f"Error processing input with llamacpp.cpp: {str(e)}")
            raise
