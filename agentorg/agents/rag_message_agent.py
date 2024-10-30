import os
import logging
from typing import List, TypedDict, Annotated
import pickle
from openai import OpenAI

from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

from .agent import BaseAgent, register_agent
from .message_agent import MessageAgent
from .rag_agent import Retriever, RAGenerator
from .message import ConvoMessage, OrchestratorMessage
from .prompts import rag_generator_prompt, retrieve_contextualize_q_prompt
from ..utils.utils import chunk_string


logger = logging.getLogger(__name__)


MODEL = {
    "model_type_or_path": "gpt-4o",
    "context": 16000,
    "max_tokens": 4096,
    "tokenizer": "o200k_base"
    }

class RagMsgState(TypedDict):
    # input message
    user_message: ConvoMessage
    orchestrator_message: OrchestratorMessage
    # message flow between different nodes
    message_flow: Annotated[str, "message flow between different nodes"]


@register_agent
class RagMsgAgent(BaseAgent):

    description = "A combination of RAG and Message Agent"

    def __init__(self, user_message: ConvoMessage, orchestrator_message: OrchestratorMessage):
        super().__init__()
        self.user_message = user_message
        self.orchestrator_message = orchestrator_message
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
     
    def _create_action_graph(self):
        workflow = StateGraph(RagMsgState)
        # Add nodes for each agent
        retriever_tool = Retriever(user_message=self.user_message, orchestrator_message=self.orchestrator_message)
        generator_tool = RAGenerator(user_message=self.user_message, orchestrator_message=self.orchestrator_message)
        msg_tool = MessageAgent(user_message=self.user_message, orchestrator_message=self.orchestrator_message)
        workflow.add_node("retriever", retriever_tool.retrieve)
        workflow.add_node("rag_generator", generator_tool.rag_generator)
        workflow.add_node("message_generator", msg_tool.generator)
        # Add edges
        workflow.add_edge(START, "retriever")
        workflow.add_edge("retriever", "rag_generator")
        workflow.add_edge("rag_generator", "message_generator")
        return workflow

    def execute(self):
        graph = self.action_graph.compile()
        result = graph.invoke({"user_message": self.user_message, "orchestrator_message": self.orchestrator_message, "message_flow": ""})
        return result
    

if __name__ == "__main__":
    user_message = ConvoMessage(history="", message="How can you help me?")
    orchestrator_message = OrchestratorMessage(message="What is your name?", attribute={"direct_response": False})
    agent = RagMsgAgent(user_message=user_message, orchestrator_message=orchestrator_message)
    result = agent.execute()
    print(result)