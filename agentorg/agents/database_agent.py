## TODO: test all agents and tool generator
import logging

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agentorg.agents.agent import BaseAgent, register_agent
from agentorg.agents.prompts import database_action_prompt
from agentorg.agents.tools.RAG.utils import ToolGenerator
from agentorg.agents.tools.database.utils import DatabaseActions
from agentorg.agents.message_agent import MessageAgent
from agentorg.utils.utils import chunk_string
from agentorg.utils.graph_state import MessageState, StatusEnum
from agentorg.utils.model_config import MODEL



logger = logging.getLogger(__name__)


@register_agent
class DatabaseAgent(BaseAgent):

    description = "Help the user with actions related to customer support like a booking system with structured data, always involving search, insert, update, and delete operations."

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
        self.actions = {
            "SearchShow": "Search for shows", 
            "BookShow": "Book a show", 
            "CheckBooking": "Check details of booked show(s)",
            "CancelBooking": "Cancel a booking",
            "Others": "Other actions not mentioned above"
        }
        self.DBActions = DatabaseActions()
        self.action_graph = self._create_action_graph()

    def search_show(self, state: MessageState):
        return self.DBActions.search_show(state)
    
    def book_show(self, state: MessageState):
        return self.DBActions.book_show(state)
    
    def check_booking(self, state: MessageState):
        return self.DBActions.check_booking(state)
    
    def cancel_booking(self, state: MessageState):
        return self.DBActions.cancel_booking(state)

    def verify_action(self, msg_state: MessageState):
        user_intent = msg_state["orchestrator_message"].attribute.get("task", "")
        actions_info = "\n".join([f"{name}: {description}" for name, description in self.actions.items()])
        actions_name = ", ".join(self.actions.keys())

        prompt = PromptTemplate.from_template(database_action_prompt)
        input_prompt = prompt.invoke({"user_intent": user_intent, "actions_info": actions_info, "actions_name": actions_name})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        logger.info(f"Chunked prompt for deciding choosing DB action: {chunked_prompt}")
        final_chain = self.llm | StrOutputParser()
        try:
            answer = final_chain.invoke(chunked_prompt)
            for action_name in self.actions.keys():
                if action_name in answer:
                    logger.info(f"Chosen action in the database agent: {action_name}")
                    return action_name
            logger.info(f"Base action chosen in the database agent: Others")
            return "Others"
        except Exception as e:
            logger.error(f"Error occurred while choosing action in the database agent: {e}")
            return "Others"
        
    def check_task_status(self, state: MessageState):
        task_status = state.get("status", StatusEnum.COMPLETE)
        if task_status == StatusEnum.COMPLETE:
            return END
        logger.info("Task is not complete, responded by MessageAgent with message flow")
        return "message_agent"
        
    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        msg_agt = MessageAgent()
        # Add nodes for each agent
        workflow.add_node("SearchShow", self.search_show)
        workflow.add_node("BookShow", self.book_show)
        workflow.add_node("CheckBooking", self.check_booking)
        workflow.add_node("CancelBooking", self.cancel_booking)
        workflow.add_node("Others", ToolGenerator.generate)
        workflow.add_node("message_agent", msg_agt.execute)
        workflow.add_conditional_edges(START, self.verify_action)
        workflow.add_conditional_edges("SearchShow", self.check_task_status)
        workflow.add_conditional_edges("BookShow", self.check_task_status)
        workflow.add_conditional_edges("CheckBooking", self.check_task_status)
        workflow.add_conditional_edges("CancelBooking", self.check_task_status)
        return workflow

    def execute(self, msg_state: MessageState):
        self.DBActions.log_in()
        self.DBActions.init_slots(msg_state["slots"])
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        return result
