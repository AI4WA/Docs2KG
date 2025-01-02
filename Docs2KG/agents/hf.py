from typing import Any

from Docs2KG.agents.base import BaseAgent


class HuggingFaceAgent(BaseAgent):
    def process(self, input_data: Any) -> Any:
        return f"HuggingFace Agent {self.name} processed: {input_data}"
