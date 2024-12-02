import logging
import os

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from agentorg.agents.agent import BaseAgent, register_agent, AGENT_REGISTRY
from agentorg.agents.prompts import choose_agent_prompt
from agentorg.utils.utils import chunk_string
from agentorg.utils.graph_state import MessageState
from agentorg.utils.model_config import MODEL


logger = logging.getLogger(__name__)


@register_agent
class DefaultAgent(BaseAgent):

    description = "Default Agent if there is no specific agent for the user's query"

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        self.base_choice = "MessageAgent"
        available_agents = os.getenv("AVAILABLE_AGENTS", "").split(",")
        self.available_agents = {name: AGENT_REGISTRY[name].description for name in available_agents if name != "DefaultAgent"}

    def _choose_agent(self, state: MessageState, limit=2):
        user_message = state['user_message']
        task = state["orchestrator_message"].attribute.get("task", "")
        agents_info = "\n".join([f"{name}: {description}" for name, description in self.available_agents.items()])
        agents_name = ", ".join(self.available_agents.keys())

        prompt = PromptTemplate.from_template(choose_agent_prompt)
        input_prompt = prompt.invoke({"message": user_message.message, "formatted_chat": user_message.history, "task": task, "agents_info": agents_info, "agents_name": agents_name})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        final_chain = self.llm | StrOutputParser()
        while limit > 0:
            answer = final_chain.invoke(chunked_prompt)
            for agent_name in self.available_agents.keys():
                if agent_name in answer:
                    logger.info(f"Chosen agent for the default agent: {agent_name}")
                    return agent_name
            limit -= 1
        logger.info(f"Base agent chosen for the default agent: {self.base_choice}")
        return self.base_choice
    
    def execute(self, msg_state: MessageState):
        chose_agent = self._choose_agent(msg_state)
        agent = AGENT_REGISTRY[chose_agent]()
        result = agent.execute(msg_state)
        return result
