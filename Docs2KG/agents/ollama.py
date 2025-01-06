from typing import Any

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry

from Docs2KG.agents.base import BaseAgent
from Docs2KG.utils.config import PROJECT_CONFIG


class OllamaAgent(BaseAgent):
    def __init__(self, name: str):
        """
        Initialize OllamaAgent with model name and optional API base URL.

        Args:
            name: Name of the Ollama model to use (e.g., 'llama2', 'mistral')
        """
        super().__init__(name)
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        """Initialize requests session with retries and timeouts"""
        try:
            session = requests.Session()

            # Configure retries
            retries = Retry(
                total=PROJECT_CONFIG.ollama.max_retries,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504],
            )

            # Set up the session with retry configuration
            session.mount("http://", HTTPAdapter(max_retries=retries))
            session.mount("https://", HTTPAdapter(max_retries=retries))

            # Set base URL
            self.api_base = PROJECT_CONFIG.ollama.api_base

            logger.info(
                f"Successfully initialized Ollama session for model {self.name}"
            )
            return session

        except Exception as e:
            logger.error(f"Failed to initialize Ollama session: {str(e)}")
            raise

    def reset_session(self):
        """Reset the requests session"""
        self.session.close()
        self.session = self._init_session()

    def process(self, input_data: Any, reset_session: bool = False) -> Any:
        """
        Process input using the Ollama API.

        Args:
            input_data: The input to be processed by the model
            reset_session: Whether to reset the requests session before making the API call

        Returns:
            Dict containing the model response and metadata
        """
        logger.info(f"Using Ollama model: {self.name}")

        try:
            # Prepare the request
            url = f"{self.api_base}/api/generate"

            payload = {
                "model": self.name,
                "prompt": str(input_data),
                "temperature": PROJECT_CONFIG.ollama.temperature,
                "stream": False,
                "format": PROJECT_CONFIG.ollama.format,
            }

            # Make the API call
            if reset_session:
                self.reset_session()
            response = self.session.post(
                url, json=payload, timeout=PROJECT_CONFIG.ollama.timeout
            )
            response.raise_for_status()

            result = response.json()

            return {
                "model": self.name,
                "input": input_data,
                "status": "processed",
                "response": result.get("response", ""),
                "usage": {
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                    "total_duration": result.get("total_duration", 0),
                },
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Ollama API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing input with Ollama: {str(e)}")
            raise
