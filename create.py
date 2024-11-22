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

logger = init_logger(log_level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), "logs", "agenorg.log"))

API_PORT = "55135"
NLUAPI_ADDR = f"http://localhost:{API_PORT}/nlu/predict"
SLOTFILLAPI_ADDR = f"http://localhost:{API_PORT}/slotfill/predict"

def generate_taskgraph(args):
    model = ChatOpenAI(model="gpt-4o", timeout=30000)
    generator = Generator(args, args.config, model, args.output_dir)
    taskgraph_filepath = generator.generate()
    # Update the task graph with the API URLs
    task_graph = json.load(open(os.path.join(os.path.dirname(__file__), taskgraph_filepath)))
    task_graph["nluapi"] = NLUAPI_ADDR
    task_graph["slotfillapi"] = SLOTFILLAPI_ADDR
    with open(taskgraph_filepath, "w") as f:
        json.dump(task_graph, f, indent=4)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="./agentorg/orchestrator/examples/customer_service_config.json")
    parser.add_argument('--output-dir', type=str, default="./examples/test")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)
    
    generate_taskgraph(args)