import os
import json
import argparse
import time
import logging
import subprocess
import signal
import atexit

from langchain_openai.chat_models import ChatOpenAI

from agentorg.utils.utils import init_logger
from agentorg.orchestrator.orchestrator import AgentOrg
from agentorg.orchestrator.generator.generator import Generator

logger = init_logger(log_level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), "logs", "agenorg.log"))

process = None  # Global reference for the FastAPI subprocess
API_PORT = 55135
NLUAPI_ADDR = f"http://localhost:{API_PORT}/nlu/predict"
SLOTFILLAPI_ADDR = f"http://localhost:{API_PORT}/slotfill/predict"

def terminate_subprocess():
    """Terminate the FastAPI subprocess."""
    global process
    if process and process.poll() is None:  # Check if process is running
        logger.info(f"Terminating FastAPI process with PID: {process.pid}")
        process.terminate()  # Send SIGTERM
        process.wait()  # Ensure it stops
        logger.info("FastAPI process terminated.")

# Register cleanup function to run on program exit
atexit.register(terminate_subprocess)

# Handle signals (e.g., Ctrl+C)
signal.signal(signal.SIGINT, lambda signum, frame: exit(0))
signal.signal(signal.SIGTERM, lambda signum, frame: exit(0))


def get_api_bot_response(args, history, user_text, parameters):
    data = {"text": user_text, 'chat_history': history, 'parameters': parameters}
    orchestrator = AgentOrg(config=os.path.join(os.path.dirname(__file__), args.config_taskgraph))
    result = orchestrator.get_response(data)

    return result['answer'], result['parameters']


def start_apis(config_taskgraph):
    """Start the FastAPI subprocess and update task graph API URLs."""
    global process
    task_graph = json.load(open(os.path.join(os.path.dirname(__file__), config_taskgraph)))
    
    command = [
        "uvicorn",
        "agentorg.orchestrator.NLU.api:app",  # Replace with proper import path
        "--port", "55135",
        "--host", "0.0.0.0",
        "--log-level", "info"
    ]

    # Redirect FastAPI logs to a file
    with open("./logs/api.log", "w") as log_file:
        process = subprocess.Popen(
            command,
            stdout=log_file,  # Redirect stdout to a log file
            stderr=subprocess.STDOUT,  # Redirect stderr to the same file
            start_new_session=True  # Run in a separate process group
        )
    logger.info(f"Started FastAPI process with PID: {process.pid}")

    task_graph["nluapi"] = NLUAPI_ADDR
    task_graph["slotfillapi"] = SLOTFILLAPI_ADDR

    with open(config_taskgraph, "w") as f:
        json.dump(task_graph, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, default="apprentice", choices=["novice", "apprentice"])
    parser.add_argument('--config', type=str, default="./agentorg/orchestrator/examples/customer_service_config.json")
    parser.add_argument('--config-taskgraph', type=str, default="./agentorg/orchestrator/examples/default_taskgraph.json")
    args = parser.parse_args()
    
    if args.type == "novice":
        model = ChatOpenAI(model="gpt-4o", timeout=30000)
        generator = Generator(args.config, model)
        args.config_taskgraph = generator.generate()
        # Initialize NLU and Slotfill APIs
        start_apis(args.config_taskgraph)
        
    history = []
    params = {}
    config = json.load(open(os.path.join(os.path.dirname(__file__), args.config_taskgraph)))
    user_prefix = "USER"
    agent_prefix = "ASSISTANT"
    for node in config['nodes']:
        if node[1].get("type", "") == 'start':
            start_message = node[1]['attribute']["value"]
            break
    history.append({"role": agent_prefix, "content": start_message})
    print(f"Bot: {start_message}")
    try:
        while True:
            user_text = input("You: ")
            if user_text.lower() == "quit":
                break
            start_time = time.time()
            output, params = get_api_bot_response(args, history, user_text, params)
            history.append({"role": user_prefix, "content": user_text})
            history.append({"role": agent_prefix, "content": output})
            print(f"getAPIBotResponse Time: {time.time() - start_time}")
            print(f"Bot: {output}")
    finally:
        terminate_subprocess()  # Ensure the subprocess is terminated
