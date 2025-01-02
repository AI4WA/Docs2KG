from typing import Any, Dict, Optional

import requests
from loguru import logger
from requests.adapters import HTTPAdapter, Retry

from Docs2KG.agents.base import BaseAgent
from Docs2KG.agents.config import OLLAMA_MODEL_CONFIGS


class OllamaAgent(BaseAgent):
    def __init__(self, name: str, api_base: Optional[str] = None):
        """
        Initialize OllamaAgent with model name and optional API base URL.

        Args:
            name: Name of the Ollama model to use (e.g., 'llama2', 'mistral')
            api_base: Optional API base URL. If not provided, will use default from config
        """
        super().__init__(name)
        self.model = self._init_model_config()
        self.session = self._init_session(api_base)

    def _init_model_config(self) -> Dict[str, Any]:
        """Initialize model configuration from predefined configs"""
        model_name = self.name.lower()
        config = OLLAMA_MODEL_CONFIGS.get(model_name)
        if not config:
            logger.error(f"No configuration found for model: {model_name}")
            raise ValueError(f"Invalid model name: {model_name}")
        return config

    def _init_session(self, api_base: Optional[str] = None) -> requests.Session:
        """Initialize requests session with retries and timeouts"""
        try:
            session = requests.Session()

            # Configure retries
            retries = Retry(
                total=self.model.get("max_retries", 2),
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504],
            )

            # Set up the session with retry configuration
            session.mount("http://", HTTPAdapter(max_retries=retries))
            session.mount("https://", HTTPAdapter(max_retries=retries))

            # Set base URL
            self.api_base = api_base or self.model.get(
                "api_base", "http://localhost:11434"
            )

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
        logger.info(f"Using Ollama model: {self.model['model']}")
        logger.info(f"Processing with configurations: {self.model}")

        try:
            # Prepare the request
            url = f"{self.api_base}/api/generate"

            payload = {
                "model": self.model["model"],
                "prompt": str(input_data),
                "temperature": self.model.get("temperature", 0.7),
                "stream": False,
                "format": self.model.get("format", "json"),
            }

            # Add optional parameters if they exist in config
            for param in ["num_ctx", "top_k", "top_p", "num_predict"]:
                if param in self.model:
                    payload[param] = self.model[param]

            # Make the API call
            if reset_session:
                self.reset_session()
            response = self.session.post(
                url, json=payload, timeout=self.model.get("timeout", 30)
            )
            response.raise_for_status()

            result = response.json()

            return {
                "model": self.model["model"],
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
