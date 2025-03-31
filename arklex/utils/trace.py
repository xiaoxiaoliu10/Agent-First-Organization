from enum import Enum
import copy

class TraceRunName(str, Enum):
    TaskGraph = "TaskGraph"
    ExecutionResult = "ExecutionResult"
    OrchestResponse = "OrchestResponse"
    NLU = "NLU"
    SlotFilling = "SlotFilling"


def format_meta(response_state, params, node_info=None, env=None):
    if not node_info:
        tool_info = None
        tool_input = None
    else:
        tool_info = node_info
        tool_id = node_info["id"]
        if tool_id in env.tools:
            tool_name = env.tools[tool_id]["name"]
            tool_input = response_state["slots"][tool_name]
        else:
            tool_input = None

        
    tool_output = response_state.get("response", "") or response_state.get("message_flow", "")
    tool_response = copy.deepcopy(response_state.get("metadata", {}).get("tool_response", {}))
    params["metadata"]["tool_response"].append({
        "tool_info": tool_info,
        "tool_input": tool_input,
        "tool_output": tool_output,
        "tool_inter": tool_response
    })
    return params