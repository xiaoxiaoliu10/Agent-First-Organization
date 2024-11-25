# MessageAgent
## Introduction

Message Agents are the basis of the rest of the agents and is responsible for the handling the chat response of the bot. Essential to nearly every conversational component, it can be combined with other agents to create integrate more complicated processes into the conversation.

# Implementation
```py
class BaseAgent(ABC):
    
    description = None

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"
    
    @abstractmethod
    def execute(self):
        pass
```