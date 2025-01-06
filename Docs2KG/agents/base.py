from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        pass
