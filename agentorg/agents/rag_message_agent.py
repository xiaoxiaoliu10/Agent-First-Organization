import logging

from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

from agentorg.agents.agent import BaseAgent, register_agent
from agentorg.agents.message_agent import MessageAgent
from agentorg.agents.rag_agent import RAGAgent
from agentorg.utils.graph_state import MessageState


logger = logging.getLogger(__name__)


@register_agent
class RagMsgAgent(BaseAgent):

    description = "A combination of RAG and Message Agent"

    def __init__(self):
        super().__init__()
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
     
    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        # Add nodes for each agent
        rag_agt = RAGAgent()
        msg_agt = MessageAgent()
        workflow.add_node("rag_agent", rag_agt.execute)
        workflow.add_node("message_agent", msg_agt.execute)
        # Add edges
        workflow.add_edge(START, "rag_agent")
        workflow.add_edge("rag_agent", "message_agent")
        return workflow

    def execute(self, msg_state: MessageState):
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        return result
