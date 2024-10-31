from typing import TypedDict, Annotated
from ..agents.message import ConvoMessage, OrchestratorMessage


class MessageState(TypedDict):
    # input message
    user_message: ConvoMessage
    orchestrator_message: OrchestratorMessage
    # message flow between different nodes
    message_flow: Annotated[str, "message flow between different nodes"]