import os
import logging
from typing import List
import pickle

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools import TavilySearchResults

from agentorg.env.prompts import context_generator_prompt, retrieve_contextualize_q_prompt, generator_prompt
from agentorg.utils.utils import chunk_string
from agentorg.utils.graph_state import MessageState
from agentorg.utils.model_config import MODEL


logger = logging.getLogger(__name__)


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
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        self.retriever = self._init_retriever()

    def _init_retriever(self, **kwargs):
        # initiate FAISS retriever
        embedding_model = OpenAIEmbeddings(
            model=self.embedding_model_name,
        )
        docsearch = FAISS.from_documents(self.texts, embedding_model)
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
        logger.info(f"Reformulated input for retriever search: {ret_input}")
        docs_and_score = self.retrieve_w_score(ret_input)
        retrieved_text = ""
        for doc, score in docs_and_score:
            retrieved_text += f"{doc.page_content} \n"
        return retrieved_text

    @staticmethod
    def load_docs(database_path: str, embeddings: str=None, index_path: str="./index"):
        document_path = os.path.join(database_path, "chunked_documents.pkl")
        index_path = os.path.join(database_path, "index")
        logger.info(f"Loaded documents from {document_path}")
        with open(document_path, 'rb') as fread:
            documents = pickle.load(fread)
        logger.info(f"Loaded {len(documents)} documents")

        return FaissRetriever(
            texts=documents,
            index_path=index_path
        )
    

class RetrieveEngine():
    @staticmethod
    def retrieve(state: MessageState):
        # get the input message
        user_message = state['user_message']

        # Search for the relevant documents
        docs = FaissRetriever.load_docs(database_path=os.environ.get("DATA_DIR"))
        retrieved_text = docs.search(user_message.history)

        state["message_flow"] = retrieved_text
        return state


class SearchEngine():
    def __init__(self):
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
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
        state["message_flow"] = self.process_search_result(search_results)
        return state
    

class ToolGenerator():
    @staticmethod
    def generate(state: MessageState):
        user_message = state['user_message']
        
        llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        prompt = PromptTemplate.from_template(generator_prompt)
        input_prompt = prompt.invoke({"sys_instruct": state["sys_instruct"], "formatted_chat": user_message.history})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        final_chain = llm | StrOutputParser()
        answer = final_chain.invoke(chunked_prompt)

        state["response"] = answer
        return state

    @staticmethod
    def context_generate(state: MessageState):
        llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
        # get the input message
        user_message = state['user_message']
        message_flow = state['message_flow']
        logger.info(f"Retrieved texts (from retriever to generator): {message_flow}")
        
        # generate answer based on the retrieved texts
        prompt = PromptTemplate.from_template(context_generator_prompt)
        input_prompt = prompt.invoke({"sys_instruct": state["sys_instruct"], "formatted_chat": user_message.history, "context": message_flow})
        chunked_prompt = chunk_string(input_prompt.text, tokenizer=MODEL["tokenizer"], max_length=MODEL["context"])
        final_chain = llm | StrOutputParser()
        logger.info(f"Prompt: {input_prompt.text}")
        answer = final_chain.invoke(chunked_prompt)
        state["message_flow"] = ""
        state["response"] = answer

        return state