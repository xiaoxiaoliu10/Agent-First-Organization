from enum import Enum

class TraceRunName(str, Enum):
    TaskGraph = "TaskGraph"
    ExecutionResult = "ExecutionResult"
    OrchestResponse = "OrchestResponse"
