class AgentError(Exception):
    """Base exception for agent-related errors"""

    pass


class InvalidAgentType(AgentError):
    """Raised when an invalid agent type is specified"""

    pass


class ConfigurationError(AgentError):
    """Raised when there's an error in agent configuration"""

    pass
