from typing import Any, Dict

CLOUD_MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "gpt-4o": {
        "model": "gpt-4o",
        "max_tokens": 4096,
        "temperature": 0.7,
        "api_base": "https://api.openai.com/v1",
    },
    "gpt-4-turbo": {
        "model": "gpt-4-1106-preview",
        "max_tokens": 4096,
        "temperature": 0.7,
        "api_base": "https://api.openai.com/v1",
    },
}

OLLAMA_MODEL_CONFIGS = {
    "llama2": {
        "model": "llama2",
        "api_base": "http://localhost:11434",
        "timeout": 30,
        "max_retries": 2,
        "temperature": 0.7,
        "context_window": 4096,
        "format": "json",
        "stream": False,
    },
    "llama3": {
        "model": "llama3",
        "api_base": "http://localhost:11434",
        "timeout": 30,
        "max_retries": 2,
        "temperature": 0.7,
        "context_window": 81920,
        "format": "json",
        "stream": False,
    },
    "mistral": {
        "model": "mistral",
        "api_base": "http://localhost:11434",
        "timeout": 30,
        "max_retries": 2,
        "temperature": 0.7,
        "context_window": 8192,
        "format": "json",
        "stream": False,
    },
    "codellama": {
        "model": "codellama",
        "api_base": "http://localhost:11434",
        "timeout": 30,
        "max_retries": 2,
        "temperature": 0.7,
        "context_window": 16384,
        "format": "json",
        "stream": False,
    },
    "phi3.5": {
        "model": "phi3.5",
        "api_base": "http://localhost:11434",
        "timeout": 30,
        "max_retries": 2,
        "temperature": 0.7,
        "context_window": 16384,
        "format": "json",
        "stream": False,
    },
}
