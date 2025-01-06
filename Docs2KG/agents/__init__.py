# agents/__init__.py
from Docs2KG.agents.cloud import CloudAgent
from Docs2KG.agents.hf import HuggingFaceAgent
from Docs2KG.agents.manager import AgentManager
from Docs2KG.agents.quantization import QuantizationAgent

__all__ = ["AgentManager", "CloudAgent", "QuantizationAgent", "HuggingFaceAgent"]
