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

class RAGState(TypedDict):
    # input message
    user_message: ConvoMessage
    orchestrator_message: OrchestratorMessage
    # message flow between different nodes
    message_flow: Annotated[str, "message flow between different nodes"]


class FaissRetriever:
    def __init__(
            self, 
            texts: List[Document], 
            index_path: str,
            embedding_model_name: str = "text-embedding-ada-002", 
        ):
        self.texts = texts
        self.index_path = index_path
        self.embedding_model_name = embedding_model_name
        self.retriever = self._init_retriever()

    def _init_retriever(self, **kwargs):
        # initiate FAISS retriever
        embedding_model = OpenAIEmbeddings(
            model=self.embedding_model_name,
        )
        docsearch = FAISS.from_documents(self.docs, embedding_model)
        retriever = docsearch.as_retriever(**kwargs)
        return retriever     

    def retrieve_w_score(self, query: str):
        k_value = 4 if not self.retriever.search_kwargs.get('k') else self.retriever.search_kwargs.get('k')
        docs_and_scores = self.retriever.vectorstore.similarity_search_with_score(query, k=k_value)
        return docs_and_scores

    def search(self, chat_history_str: str):
        contextualize_q_prompt = PromptTemplate.from_template(
            retrieve_contextualize_q_prompt
        )
        ret_input_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        ret_input = ret_input_chain.invoke({"chat_history": chat_history_str})
        docs_and_score = self.retrieve_w_score(ret_input)
        retrieved_text = ""
        for doc, score in docs_and_score:
            retrieved_text += f"{doc.page_content} \n"
        return retrieved_text

    @staticmethod
    def load_docs(database_path: str, embeddings: str=None, index_path: str="./index"):
        document_path = os.path.join(database_path, "documents.pkl")
        index_path = os.path.join(database_path, "index")
        logger.info(f"Loaded documents from {document_path}")
        with open(document_path, 'rb') as fread:
            documents = pickle.load(fread)
        logger.info(f"Loaded {len(documents)} documents")

        return FaissRetriever(
            texts=documents,
            embedding_model_name=embeddings,
            index_path=index_path
        )


@register_agent
class RAGAgent(BaseAgent):

    description = "Answer the user's questions based on the company's internal documentations, such as the policies, FAQs, and product information"

    def __init__(self, user_message: ConvoMessage, orchestrator_message: OrchestratorMessage):
        super().__init__()
        self.user_message = user_message
        self.orchestrator_message = orchestrator_message
        self.action_graph = self._create_action_graph()
        self.llm = ChatOpenAI(model="gpt-4o", timeout=30000)

    def rag_generator(self, state: RAGState):
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
        
        prompt = PromptTemplate.from_template(rag_generator_prompt)
        chat_history_str = user_message.history + "\nUser: " + user_message.message

        # Search for the relevant documents
        docs = FaissRetriever.load_docs(database_path="./data")
        retrieved_text = docs.search(orch_msg_content)
        input_prompt = prompt.invoke({"question": orch_msg_content, "formatted_chat": chat_history_str, "context": retrieved_text})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        final_chain = self.llm | StrOutputParser()
        answer = final_chain.invoke(chunked_prompt)

        return {
            "user_message": user_message,
            "orchestrator_message": orchestrator_message,
            "message_flow": answer
        }
     
    def _create_action_graph(self):
        workflow = StateGraph(RAGState)
        # Add nodes for each agent
        workflow.add_node("rag_generator", self.rag_generator)
        # Add edges
        workflow.add_edge(START, "rag_generator")
        return workflow

    def execute(self):
        graph = self.action_graph.compile()
        result = graph.invoke({"user_message": self.user_message, "orchestrator_message": self.orchestrator_message, "message_flow": ""})
        return result