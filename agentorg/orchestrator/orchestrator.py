import json
import time
from typing import Any, Dict
import logging
import copy
import re
import datetime

from langchain.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI

from agentorg.orchestrator.base import BaseBot
from agentorg.orchestrator.task_graph import TaskGraph
from agentorg.agents.agent import AGENT_REGISTRY
from agentorg.agents.message import ConvoMessage, OrchestratorMessage
from agentorg.utils.utils import check_phone_validation, check_email_validation, possible_email
from agentorg.orchestrator.NLU.nlu import NLU
from agentorg.utils.graph_state import MessageState, StatusEnum


logger = logging.getLogger(__name__)

class AgentOrg(BaseBot):
    def __init__(self, config, model=ChatOpenAI(model="gpt-4o", timeout=30000), **kwargs):
        self.product_kwargs = json.load(open(config))
        self.user_prefix = "USER"
        self.agent_prefix = "ASSISTANT"
        self.__eos_token = "\n"
        self.tools = list(AGENT_REGISTRY.keys())
        self.task_graph = TaskGraph("taskgraph", self.product_kwargs)
        self.model = model

    def _format_chat_history(self, chat_history, text):
        '''Includes current user utterance'''
        chat_history_str= ""
        for turn in chat_history:
            chat_history_str += f"{turn['role']}: {turn['content']}{self.__eos_token}"
        chat_history_str += f"{self.user_prefix}: {text}"
        return chat_history_str.strip()

    def check_valid(self, valid_state, text):
        valid_list = self.product_kwargs.get("valid")
        lang = self.product_kwargs.get("language")
        new_valid_state = copy.deepcopy(valid_state)
        interactive_prompt = self.product_kwargs.get("question_interactive_prompt")
        for item in valid_list:
            if item["key"] == "phone":
                if not new_valid_state[item["key"]]['status'] and new_valid_state[item["key"]]['times'] < 2 and re.search(r'\d{8,11}', text) is not None:
                    text = text.replace("+", " ")
                    if not check_phone_validation(text, lang):
                        new_valid_state[item["key"]]['times'] += 1
                        interactive_prompt = interactive_prompt.format(value=item["value"])
                    else:	
                        new_valid_state[item["key"]]['status'] = True
            elif item["key"] == "email":
                if not new_valid_state[item["key"]]['status'] and new_valid_state[item["key"]]['times'] < 2 and possible_email(text):
                    if not check_email_validation(text):
                        new_valid_state[item["key"]]['times'] += 1
                        interactive_prompt = interactive_prompt.format(value=item["value"])
                    else:	
                        new_valid_state[item["key"]]['status'] = True

        interactive_prompt = interactive_prompt if interactive_prompt != self.product_kwargs.get("question_interactive_prompt") else ""
        return new_valid_state, interactive_prompt
    
    def perform_validation(self, text, params):
        valid_state = params.get("valid", {item["key"]: {"status": False, "times": 0} for item in self.product_kwargs.get("valid", [])})
        if self.product_kwargs.get("valid") and not all([s["status"] for s in valid_state.values()]):
            valid_state, interactive_prompt = self.check_valid(valid_state, text)
            logger.info(f"interactive prompt is \n{interactive_prompt}")
            params["valid"] = valid_state
            if interactive_prompt:
                return interactive_prompt, params
        return None, params
    
    def post_process(self, result, params, input_prompt):

        cleaned_result = self.answer_guardrail(result, self.bot_id, self.bot_version, input_prompt, **self.product_kwargs)
        return_result = self._prepare_output(cleaned_result, params, self.product_kwargs)

        return return_result

    def get_response(self, inputs: dict) -> Dict[str, Any]:
        st = time.time()
        text = inputs["text"]
        chat_history = inputs["chat_history"]
        params = inputs["parameters"]
        params["timing"] = {}
        chat_history_str = self._format_chat_history(chat_history, text)

        ##### Model safety checking
        # check the response, decide whether to give template response or not
        client = OpenAI()
        text = inputs["text"]
        moderation_response = client.moderations.create(input=text).model_dump()
        is_flagged = moderation_response["results"][0]["flagged"]
        if is_flagged:
            return_response = {
                "answer": self.product_kwargs["safety_response"],
                "parameters": params,
                "has_follow_up": True
            }
            return return_response

        ##### Highest level of checking without go through the dialog flow and policy planning
        # vt = time.time()
        # valid_prompt, params = self.perform_validation(text, params)
        # if valid_prompt:
        #     prompt = PromptTemplate.from_template(self.product_kwargs.get('generator_prompt_wo_tools', ""))
        #     input_prompt = prompt.invoke({"date": datetime.date.today().strftime('%B %d, %Y'), "chat_history_str": chat_history_str, "interactive_prompt": valid_prompt})
        #     final_chain = self.llm | StrOutputParser()
        #     answer = ""
        #     answer = final_chain.invoke(input_prompt)
        #     return self.post_process(answer, params, input_prompt)
        # params["timing"]["validation"] = time.time() - vt

        ##### TaskGraph Chain
        taskgraph_inputs = {
            "text": text,
            "chat_history_str": chat_history_str,
            "parameters": params,  ## TODO: different params for different components
            "model": self.model
        }
        dt = time.time()
        taskgraph_chain = RunnableLambda(self.task_graph.get_node) | RunnableLambda(self.task_graph.postprocess_node)
        node_info, params = taskgraph_chain.invoke(taskgraph_inputs)
        params["timing"]["taskgraph"] = time.time() - dt
        logger.info("=============node_info=============")
        logger.info(node_info) # {'name': 'MessageAgent', 'attribute': {'value': 'If you are interested, you can book a calendly meeting https://shorturl.at/crFLP with us. Or, you can tell me your phone number, email address, and name; our expert will reach out to you soon.', 'direct': False, 'slots': {"<name>": {<attributes>}}}}

        #### Agent execution
        user_message = ConvoMessage(history=chat_history_str, message=text)
        orchestrator_message = OrchestratorMessage(message=node_info["attribute"]["value"], attribute=node_info["attribute"])
        message_state = MessageState(user_message=user_message, orchestrator_message=orchestrator_message, message_flow="")
        agent = AGENT_REGISTRY[node_info["name"]]()
        agent_response = agent.execute(message_state)
        params["agent_response"] = agent_response

        return_answer = agent_response["message_flow"]
        node_status = params.get("node_status", {})
        current_node = params.get("curr_node")
        node_status[current_node] = {
            "status": agent_response.get("status", StatusEnum.COMPLETE),
            "slots": agent_response.get("slots", [])
        }

        params["node_status"] = node_status

        output = {
            "answer": return_answer,
            "parameters": params
        }

        return output
