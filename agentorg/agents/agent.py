from abc import ABC, abstractmethod
from agentorg.utils.graph_state import MessageState

AGENT_REGISTRY = {}

def register_agent(cls):
    """Decorator to register an agent."""
    cls.name = cls.__name__  # Automatically set name to the class name
    AGENT_REGISTRY[cls.__name__] = cls  # Register the class
    return cls


class BaseAgent(ABC):
    
    description = None

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"
    
    @abstractmethod
    def execute(self, msg_state: MessageState):
        pass
