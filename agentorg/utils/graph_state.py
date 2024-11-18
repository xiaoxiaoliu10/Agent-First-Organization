from typing import TypedDict, Annotated
from pydantic import BaseModel
from enum import Enum


class ConvoMessage(BaseModel):
    history: str # it could be the whole original message or the summarization of the previous conversation from memory module
    message: str


class OrchestratorMessage(BaseModel):
    message: str
    attribute: dict


class Slot(BaseModel):
    name: str
    type: str
    value: str
    description: str
    prompt: str


class Slots(BaseModel):
    slots: list[Slot]


class SlotDetail(Slot):
    verified_value: str
    confirmed: bool


class StatusEnum(Enum):
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"


class MessageState(TypedDict):
    # input message
    user_message: ConvoMessage
    orchestrator_message: OrchestratorMessage
    # message flow between different nodes
    message_flow: Annotated[str, "message flow between different nodes"]
    # final response
    response: str
    # task-related params
    status: StatusEnum
    slots: list[Slot]