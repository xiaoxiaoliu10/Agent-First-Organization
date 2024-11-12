## TODO: test all agents and tool generator
import logging

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .agent import BaseAgent, register_agent
from .prompts import database_action_prompt
from ..utils.utils import chunk_string
from ..utils.graph_state import MessageState
from ..utils.model_config import MODEL
from .tools.database.utils import DatabaseActions
from ..utils.graph_state import Slot


logger = logging.getLogger(__name__)


@register_agent
class DatabaseAgent(BaseAgent):

    description = "Answer the user's questions based on search engine results"

    def __init__(self):
        self.config = {"user_id": "abcd"}
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
        self.actions = {
            "SearchShow": "Search for shows", 
            "BookShow": "Book a show", 
            "CheckBooking": "Check details of booked show(s)",
            "CancelBooking": "Cancel a booking",
            "Others": "Other actions not mentioned above"
        }
        self.action_graph = self._create_action_graph()

    def verify_action(self, user_intent: str):
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
        
    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        # Add nodes for each agent
        DBFunctions = DatabaseActions()
        workflow.add_node("find_intent", self.find_user_intent)
        workflow.add_node("search_show", DBFunctions.search_show)
        workflow.add_node("book_show", DBFunctions.book_show)
        workflow.add_node("check_booking", DBFunctions.check_booking)
        workflow.add_node("cancel_booking", DBFunctions.cancel_booking)
        workflow.add_node("generator", ToolGenerator.generate)
        # Add edges
        workflow.add_edge(START, "find_intent")
        workflow.add_edge("find_intent", "search_show", lambda state: state["find_intent"] == "SearchShow")
        workflow.add_edge("find_intent", "book_show", lambda state: state["find_intent"] == "BookShow")
        workflow.add_edge("find_intent", "check_booking", lambda state: state["find_intent"] == "CheckBooking")
        workflow.add_edge("find_intent", "cancel_booking", lambda state: state["find_intent"] == "CancelBooking")
        workflow.add_edge("find_intent", "generator", lambda state: state["find_intent"] == "Others")
        workflow.add_edge("search_show", "find_intent")
        workflow.add_edge("book_show", "find_intent")
        workflow.add_edge("check_booking", "find_intent")
        workflow.add_edge("cancel_booking", "find_intent")
        workflow.add_edge("generator", END)
        return workflow

    def execute(self, msg_state: MessageState):
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        return result
