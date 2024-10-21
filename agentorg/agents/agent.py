from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"
    
    @abstractmethod
    def execute(self):
        pass
