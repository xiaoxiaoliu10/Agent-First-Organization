from typing import TypedDict, Annotated
from enum import Enum
from ..agents.message import ConvoMessage, OrchestratorMessage


class StatusEnum(Enum):
    COMPELETE = "complete"
    INCOMPLETE = "incomplete"


class SlotValues(TypedDict):
    original_value: str
    verified_value: str
    prompt: str


class Slot(TypedDict):
    name: str
    slot_type: str
    description: str
    slot_values: SlotValues
    confirmed: bool


class MessageState(TypedDict):
    # input message
    user_message: ConvoMessage
    orchestrator_message: OrchestratorMessage
    # message flow between different nodes
    message_flow: Annotated[str, "message flow between different nodes"]
    status: StatusEnum
    slots: list