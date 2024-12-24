import os
import json
import argparse
import time
import logging
import subprocess
import signal
import atexit

from langchain_openai import ChatOpenAI

from agentorg.utils.utils import init_logger
from agentorg.orchestrator.orchestrator import AgentOrg
from agentorg.orchestrator.generator.generator import Generator
from agentorg.tools.RAG.build_rag import build_rag
from agentorg.tools.database.build_database import build_database
from agentorg.utils.model_config import MODEL

logger = init_logger(log_level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), "logs", "agentorg.log"))

API_PORT = "55135"
NLUAPI_ADDR = f"http://localhost:{API_PORT}/nlu/predict"
SLOTFILLAPI_ADDR = f"http://localhost:{API_PORT}/slotfill/predict"

def generate_taskgraph(args):
    model = ChatOpenAI(model=MODEL["model_type_or_path"], timeout=30000)
    generator = Generator(args, args.config, model, args.output_dir)
    taskgraph_filepath = generator.generate()
    # Update the task graph with the API URLs
    task_graph = json.load(open(os.path.join(os.path.dirname(__file__), taskgraph_filepath)))
    task_graph["nluapi"] = NLUAPI_ADDR
    task_graph["slotfillapi"] = SLOTFILLAPI_ADDR
    with open(taskgraph_filepath, "w") as f:
        json.dump(task_graph, f, indent=4)


def init_worker(args):
    # Customized based on your worker design
    config = json.load(open(args.config))
    workers = config["workers"]
    if "RAGWorker" in workers:
        logger.info("Initializing RAGWorker...")
        build_rag(args.output_dir, config["rag_docs"])

    elif "DataBaseWorker" in workers:
        logger.info("Initializing DataBaseWorker...")
        build_database(args.output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="./agentorg/orchestrator/examples/customer_service_config.json")
    parser.add_argument('--output-dir', type=str, default="./examples/test")
    parser.add_argument('--model', type=str, default=MODEL["model_type_or_path"])
    parser.add_argument('--log-level', type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    args = parser.parse_args()
    MODEL["model_type_or_path"] = args.model
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger = init_logger(log_level=log_level, filename=os.path.join(os.path.dirname(__file__), "logs", "agentorg.log"))

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    
    generate_taskgraph(args)
    init_worker(args)