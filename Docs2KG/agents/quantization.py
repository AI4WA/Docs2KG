from typing import Any

from Docs2KG.agents.base import BaseAgent


class QuantizationAgent(BaseAgent):
    def process(self, input_data: Any) -> Any:
        return f"Quantization Agent {self.name} processed: {input_data}"
