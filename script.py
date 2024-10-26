import os
import json
import argparse
import time

from agentorg.orchestrator.orchestrator import AgentOrg


def get_api_bot_response(args, history, user_text, parameters):
	data = {"text": user_text, 'chat_history': history, 'parameters': parameters}
	orchestrator = AgentOrg(config=os.path.join(os.path.dirname(__file__), args.config))
	result = orchestrator.get_response(data)

	return result['answer'], result['parameters']



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="./agentorg/orchestrator/examples/default.json")
    args = parser.parse_args()
    
    history = []
    params = {}
    config = json.load(open(os.path.join(os.path.dirname(__file__), args.config)))
    user_prefix = config['user_prefix']
    agent_prefix = config['agent_prefix']
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