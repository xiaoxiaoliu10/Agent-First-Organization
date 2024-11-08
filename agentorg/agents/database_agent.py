from .agent import BaseAgent, register_agent
from .message import ConvoMessage, OrchestratorMessage

@register_agent
class DatabaseAgent(BaseAgent):

    description = "Access the company's database to retrieve information about products, such as availability, pricing, and specifications"

    def __init__(self, user_message: ConvoMessage, orchestrator_message: OrchestratorMessage):
        super().__init__()

    def execute(self):
        raise NotImplementedError

    