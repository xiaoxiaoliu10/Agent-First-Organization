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
from agentorg.agents.tools.RAG.build_rag import build_rag
from agentorg.agents.tools.database.build_database import build_database
from agentorg.utils.model_config import MODEL

logger = init_logger(log_level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), "logs", "agenorg.log"))

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


def init_agent(args):
    # Customized based on your agent design
    config = json.load(open(args.config))
    agents = config["agents"]
    if "RAGAgent" in agents:
        logger.info("Initializing RAGAgent...")
        build_rag(args.output_dir, config["rag_docs"])

    elif "DatabaseAgent" in agents:
        logger.info("Initializing DatabaseAgent...")
        build_database(args.output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="./agentorg/orchestrator/examples/customer_service_config.json")
    parser.add_argument('--output-dir', type=str, default="./examples/test")
    parser.add_argument('--model', type=str, default=MODEL["model_type_or_path"])
    args = parser.parse_args()
    MODEL["model_type_or_path"] = args.model

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    
    generate_taskgraph(args)
    init_agent(args)