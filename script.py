import os
import json
import argparse
import time
import logging

from langchain_openai.chat_models import ChatOpenAI

from agentorg.utils.utils import init_logger
from agentorg.orchestrator.orchestrator import AgentOrg
from agentorg.orchestrator.generator.autogen import AutoGen

logger = init_logger(log_level=logging.INFO, filename=os.path.join(os.path.dirname(__file__), "logs", "agenorg.log"))


def get_api_bot_response(args, history, user_text, parameters):
	data = {"text": user_text, 'chat_history': history, 'parameters': parameters}
	orchestrator = AgentOrg(config=os.path.join(os.path.dirname(__file__), args.config_taskgraph))
	result = orchestrator.get_response(data)

	return result['answer'], result['parameters']



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=str, default="apprentice", choices=["novice", "apprentice"])
    parser.add_argument('--config', type=str, default="./agentorg/orchestrator/examples/customer_service_config.json")
    parser.add_argument('--config-taskgraph', type=str, default="./agentorg/orchestrator/examples/default_taskgraph.json")
    args = parser.parse_args()
    
    if args.type == "novice":
        model = ChatOpenAI(model="gpt-4o", timeout=30000)
        autogen = AutoGen(args.config, model)
        args.config_taskgraph = autogen.generate()

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
    while True:
        user_text = input("You: ")
        if user_text == "quit":
            break
        start_time = time.time()
        output, params = get_api_bot_response(args, history, user_text, params)
        history.append({"role": user_prefix, "content": user_text})
        history.append({"role": agent_prefix, "content": output})
        print(f"getAPIBotResponse Time: {time.time() - start_time}")
        print(f"Bot: {output}")