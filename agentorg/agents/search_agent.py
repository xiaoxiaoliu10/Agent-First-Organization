import logging

from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import TavilySearchResults

from .agent import BaseAgent, register_agent
from .prompts import rag_generator_prompt, retrieve_contextualize_q_prompt
from ..utils.utils import chunk_string
from ..utils.graph_state import MessageState
from ..utils.model_config import MODEL


logger = logging.getLogger(__name__)


class SearchEngine():
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
        self.search_tool = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=False,
        )

    def process_search_result(self, search_results):
        search_text = ""
        for res in search_results:
            search_text += f"Source: {res['url']} \n"
            search_text += f"Content: {res['content']} \n\n"
        return search_text

    def search(self, state: MessageState):
        contextualize_q_prompt = PromptTemplate.from_template(
            retrieve_contextualize_q_prompt
        )
        ret_input_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        ret_input = ret_input_chain.invoke({"chat_history": state["user_message"].history})
        logger.info(f"Reformulated input for search engine: {ret_input}")
        search_results = self.search_tool.invoke({"query": ret_input})
        return {
            "user_message": state["user_message"],
            "orchestrator_message": state["orchestrator_message"],
            "message_flow": self.process_search_result(search_results)
        }
    

class SearchGenerator():
    @staticmethod
    def search_generate(state: MessageState):
        llm = ChatOpenAI(model="gpt-4o", timeout=30000)
        # get the input message
        user_message = state['user_message']
        message_flow = state['message_flow']
        logger.info(f"Searched results (from search engine to generator): {message_flow}")
        
        # generate answer based on the searched results
        prompt = PromptTemplate.from_template(rag_generator_prompt)
        input_prompt = prompt.invoke({"question": user_message.message, "formatted_chat": user_message.history, "context": message_flow})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        final_chain = llm | StrOutputParser()
        answer = final_chain.invoke(chunked_prompt)

        return {
            "user_message": user_message,
            "orchestrator_message": state["orchestrator_message"],
            "message_flow": answer
        }


@register_agent
class SearchAgent(BaseAgent):

    description = "Answer the user's questions based on search engine results"

    def __init__(self):
        super().__init__()
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)
     
    def _create_action_graph(self):
        workflow = StateGraph(MessageState)
        # Add nodes for each agent
        search_engine = SearchEngine()
        workflow.add_node("search_engine", search_engine.search)
        workflow.add_node("search_generator", SearchGenerator.search_generate)
        # Add edges
        workflow.add_edge(START, "search_engine")
        workflow.add_edge("search_engine", "search_generator")
        return workflow

    def execute(self, msg_state: MessageState):
        graph = self.action_graph.compile()
        result = graph.invoke(msg_state)
        return result
