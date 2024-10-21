from pydantic import BaseModel


class ConvoMessage(BaseModel):
    history: str # it could be the whole original message or the summarization of the previous conversation from memory module
    message: str


class OrchestratorMessage(BaseModel):
    message: str
    attribute: dict