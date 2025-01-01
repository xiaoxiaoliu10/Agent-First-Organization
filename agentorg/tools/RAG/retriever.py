import time
from typing import List
import logging

import numpy as np
from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai.chat_models import ChatOpenAI

from agentorg.workers.prompts import load_prompts
from agentorg.utils.mysql import mysql_pool
from agentorg.utils.model_config import MODEL
from agentorg.tools.RAG.retrievers.milvus_retriever import MilvusRetriever
from agentorg.tools.RAG.retrievers.retriever_document import RetrieverResult

logger = logging.getLogger(__name__)


class RetrieverExecutor:
    def __init__(self, bot_config):
        self.bot_config = bot_config
        self.llm = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)

    def generate_thought(self, retriever_results: List[RetrieverResult]) -> str:
        # post process list of documents into str
        retrieved_str = ""
        for doc in retriever_results:
            if doc.metadata.get("title"):
                retrieved_str += "title: " + doc.metadata["title"] + "\n"
            if doc.metadata.get("source"):
                retrieved_str += "source: " + doc.metadata["source"] + "\n"
            retrieved_str += "content: " + doc.text + "\n\n"
        return retrieved_str

    def _gaussian_similarity(self, distance, sigma=0.5):
        similarity = np.exp(-(distance**2) / (2 * sigma**2)) * 100
        return round(float(similarity), 2)

    def postprocess(self, retriever_results: List[RetrieverResult]):
        retriever_returns = []
        for doc in retriever_results:
            confidence_score = self._gaussian_similarity(doc.distance)
            item = {
                "qa_doc_id": doc.qa_doc_id,
                "qa_doc_type": doc.qa_doc_type.value,
                "title": doc.metadata.get("title"),
                "content": doc.text,
                "source": doc.metadata.get("source"),
                "raw_score": round(float(doc.distance), 4),
                "confidence": confidence_score,
            }
            retriever_returns.append(item)
        return {"retriever": retriever_returns}

    def retrieve(self, chat_history_str):
        """Given a chat history, retrieve relevant information from the database."""
        st = time.time()
        prompts = load_prompts(self.bot_config)
        contextualize_q_prompt = PromptTemplate.from_template(
            prompts.get("retrieve_contextualize_q_prompt", "")
        )
        ret_input_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        ret_input = ret_input_chain.invoke({"chat_history": chat_history_str})
        rit = time.time() - st

        ret_results: List[RetrieverResult] = []
        st = time.time()
        milvus_db = mysql_pool.fetchone("SELECT collection_name FROM qa_bot WHERE id=%s AND version=%s", (self.bot_config.bot_id, self.bot_config.version))
        with MilvusRetriever() as retriever:
            ret_results = retriever.search(milvus_db["collection_name"], self.bot_config.bot_id, self.bot_config.version, ret_input)
        rt = time.time() - st
        logger.info(f"MilvusRetriever search took {rt} seconds")
        retriever_params = self.postprocess(ret_results)
        retriever_params["timing"] = {"retriever_input": rit, "retriever_search": rt}
        thought = self.generate_thought(ret_results)
        return thought, retriever_params
