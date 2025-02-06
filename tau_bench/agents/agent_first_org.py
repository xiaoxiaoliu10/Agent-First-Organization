
# Copyright Sierra
import os
import json
from copy import deepcopy
from typing import List, Optional, Dict, Any

from agentorg.orchestrator.orchestrator import AgentOrg
from agentorg.env.env import Env

# from tau_bench.envs.base import Env
from tau_bench.agents.base import Agent
from tau_bench.types import SolveResult, Action, RESPOND_ACTION_NAME


class AgentFirstOrg(Agent):
    def __init__(self, taskgraph_dir: str):
        self.taskgraph_dir = taskgraph_dir
        self.taskgraph_path = os.path.join(self.taskgraph_dir, "taskgraph.json")
        from tau_bench_eval import TauBenchResourceInitializer
        with open(self.taskgraph_path) as taskgraph:
            taskgraph = json.load(taskgraph)
            tau_bench_resource_initializer = TauBenchResourceInitializer()
            self.env = Env(
                tools = taskgraph.get("tools", []),
                workers = taskgraph.get("workers", []),
                slotsfillapi = taskgraph["slotfillapi"],
                resource_inizializer = tau_bench_resource_initializer
            )

            self.start_message = None
            for node in taskgraph['nodes']:
                if node[1].get("type", "") == 'start':
                    self.start_message = node[1]['attribute']["value"]
                    break

    def get_api_bot_response(self, history, user_text, parameters):
        data = {"text": user_text, 'chat_history': history, 'parameters': parameters}
        orchestrator = AgentOrg(config=self.taskgraph_path, env=self.env)
        result = orchestrator.get_response(data)
        return result['answer'], result['parameters']

    def solve(
        self, env, task_index: Optional[int] = None, max_num_steps: int = 30
    ) -> SolveResult:
        total_cost = 0.0
        env_reset_res = env.reset(task_index=task_index)
        obs = env_reset_res.observation
        info = env_reset_res.info.model_dump()
        reward = 0.0
        history = [
            {"role": "assistant", "content": self.start_message}
        ]
        messages = []
        params = {}

        user_text = obs
        
        for _ in range(max_num_steps):
            message_index = len(history)
            try:
                output, params = self.get_api_bot_response(deepcopy(history), user_text, params)
            except Exception as e:
                print("Error:", e)
            user_message = {"role": "user", "content": user_text}
            assistant_message = {"role": "assistant", "content": output}
            history.append(user_message)
            history.append(assistant_message)

            messages = params["history"]
            # print("*"*100)
            # print(messages)
            while message_index < len(messages):
                msg = messages[message_index]

                if msg.get("role") == "assistant" and not is_message_worker_tool_call(msg):
                    action = message_to_action(msg)
                    env_response = env.step(action)
                    reward = env_response.reward
                    info = {**info, **env_response.info.model_dump()}

                message_index += 1
            
            # total_cost += res._hidden_params["response_cost"]

            action = message_to_action(assistant_message)
            env_response = env.step(action)
            reward = env_response.reward
            info = {**info, **env_response.info.model_dump()}
            
            user_text = env_response.observation
            if env_response.done:
                user_message = {"role": "user", "content": user_text}
                history.append(user_message)
                break
        return SolveResult(
            reward=reward,
            info=info,
            messages=messages,
            total_cost=total_cost,
        )


def is_message_worker_tool_call(message):
    if "tool_calls" not in message: return False
    if message["tool_calls"] is None: return False
    if len(message["tool_calls"]) == 0: return False
    if "function" not in message["tool_calls"][0]: return False
    if message["tool_calls"][0]["function"] is None: return False
    return message["tool_calls"][0]["function"].get("name") == "MessageWorker"

def message_to_action(
    message: Dict[str, Any],
) -> Action:
    if "tool_calls" in message and \
            message["tool_calls"] is not None and \
            len(message["tool_calls"]) > 0 and \
            message["tool_calls"][0]["function"] is not None:
        
        tool_call = message["tool_calls"][0]
        return Action(
            name=tool_call["function"]["name"],
            kwargs=json.loads(tool_call["function"]["arguments"]),
        )
    else:
        return Action(name=RESPOND_ACTION_NAME, kwargs={"content": message["content"]})

