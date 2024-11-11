import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

from .agent import BaseAgent, register_agent
from ..utils.graph_state import MessageState
from .tools.RAG.utils import RetrieveEngine, ToolGenerator


logger = logging.getLogger(__name__)


@register_agent
class RAGAgent(BaseAgent):

    description = "Answer the user's questions based on the company's internal documentations, such as the policies, FAQs, and product information"

    def __init__(self):
        super().__init__()
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
     
    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        # Add nodes for each agent
        workflow.add_node("retriever", RetrieveEngine.retrieve)
        workflow.add_node("tool_generator", ToolGenerator.context_generate)
        # Add edges
        workflow.add_edge(START, "retriever")
        workflow.add_edge("retriever", "tool_generator")
        return workflow

    def execute(self, msg_state: MessageState):
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        return result
