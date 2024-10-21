from typing import TypedDict, List, Annotated, Sequence

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from .agent import BaseAgent
from .message import ConvoMessage, OrchestratorMessage
from .prompts import question_generator_prompt
from ..utils.utils import chunk_string

MODEL = {
    "model_type_or_path": "gpt-4o",
    "context": 16000,
    "max_tokens": 4096,
    "tokenizer": "o200k_base"
    }


class QuestionState(TypedDict):
    # input message
    user_message: ConvoMessage
    orchestrator_message: OrchestratorMessage
    # message flow between different nodes
    message_flow: Annotated[str, "message flow between different nodes"]



class QuestionAgent(BaseAgent):
    def __init__(self, user_message: ConvoMessage, orchestrator_message: OrchestratorMessage, name='QuestionAgent'):
        super().__init__(name)
        self.user_message = user_message
        self.orchestrator_message = orchestrator_message
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)

    def generator(self, state: QuestionState):
        # get the input message
        user_message = state['user_message']
        orchestrator_message = state['orchestrator_message']
        message_flow = state['message_flow']

        # get the orchestrator message content
        orch_msg_content = orchestrator_message.message
        orch_msg_attr = orchestrator_message.attribute
        direct_response = orch_msg_attr.get('direct_response', False)
        if direct_response:
            return orch_msg_content
        else:
            prompt = PromptTemplate.from_template(question_generator_prompt)
            input_prompt = prompt.invoke({"question": orch_msg_content, "formatted_chat": user_message.history + "\nUser: " + user_message.message})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        final_chain = self.llm | StrOutputParser()
        answer = final_chain.invoke(chunked_prompt)

        return {
            "user_message": user_message,
            "orchestrator_message": orchestrator_message,
            "message_flow": answer
        }

    def _create_action_graph(self):
        workflow = StateGraph(QuestionState)
        # Add nodes for each agent
        workflow.add_node("generator", self.generator)
        # Add edges
        workflow.add_edge(START, "generator")
        return workflow

    def execute(self):
        graph = self.action_graph.compile()
        result = graph.invoke({"user_message": self.user_message, "orchestrator_message": self.orchestrator_message, "message_flow": ""})
        return result
        # for output in graph.stream({"user_message": self.user_message, "orchestrator_message": self.orchestrator_message, "message_flow": ""}):
        #     for key, value in output.items():
        #         # Node
        #         print(f"Node '{key}':")
        #         # Optional: print full state at each node
        #         print(value)
        #     print("\n---\n")


if __name__ == "__main__":
    user_message = ConvoMessage(history="", message="How can you help me?")
    orchestrator_message = OrchestratorMessage(message="What is your name?", attribute={"direct_response": False})
    agent = QuestionAgent(user_message=user_message, orchestrator_message=orchestrator_message)
    result = agent.execute()
    print(result)