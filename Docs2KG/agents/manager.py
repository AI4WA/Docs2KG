from typing import Any, Dict

from loguru import logger

from Docs2KG.agents.base import BaseAgent
from Docs2KG.agents.cloud import CloudAgent
from Docs2KG.agents.exceptions import InvalidAgentType
from Docs2KG.agents.hf import HuggingFaceAgent
from Docs2KG.agents.ollama import OllamaAgent
from Docs2KG.agents.quantization import QuantizationAgent


class AgentManager:
    def __init__(self, agent_name: str, agent_type: str, **kwargs):
        """
        Initialize AgentManager with a specific agent.

        Args:
            agent_name: Name for the agent (e.g., 'gpt-4', 'gpt-4-turbo')
            agent_type: Type of agent ('cloud', 'quantization', or 'hf')
        """
        self.agent_types = {
            "cloud": CloudAgent,
            "quantization": QuantizationAgent,
            "ollama": OllamaAgent,
            "hf": HuggingFaceAgent,
        }
        self.agent_type = agent_type

        self.agent = self._init_agent(agent_name, agent_type, **kwargs)

    def _init_agent(self, agent_name: str, agent_type: str, **kwargs) -> BaseAgent:
        agent_type = agent_type.lower()
        if agent_type not in self.agent_types:
            raise InvalidAgentType(
                f"Invalid agent type. Must be one of: {', '.join(self.agent_types.keys())}"
            )

        agent_class = self.agent_types[agent_type]
        return agent_class(agent_name, **kwargs)

    def process_input(self, input_data: Any, reset_session: bool = False) -> Any:
        if self.agent_type == "ollama":
            return self.agent.process(input_data, reset_session)
        return self.agent.process(input_data)

    def get_agent_info(self) -> Dict[str, str]:
        return {
            "name": self.agent.name,
            "type": type(self.agent).__name__,
            "config": getattr(self.agent, "model", None),
        }


if __name__ == "__main__":
    # Example usage
    agent_manager = AgentManager(agent_name="gpt-4o", agent_type="cloud")
    output = agent_manager.process_input("Hello, how are you?")
    logger.info(f"Output: {output}")
    agent_manager = AgentManager(agent_name="phi3.5", agent_type="ollama")
    output = agent_manager.process_input("Hello, how are you?")
    logger.info(f"Output: {output}")

    agent_manager = AgentManager(agent_name="openai-community/gpt2", agent_type="hf")
    output = agent_manager.process_input("Hello, how are you?")
    logger.info(f"Output: {output}")

    # agent_name can be the model path
    agent_manager = AgentManager(agent_name=None, agent_type="quantization")
    output = agent_manager.process_input("Hello, how are you?")
    logger.info(f"Output: {output}")
