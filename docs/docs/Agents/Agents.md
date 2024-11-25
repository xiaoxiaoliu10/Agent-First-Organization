# Agents

Agents serve as the fundamental building block of the **AgentOrg** framework and responsible for the "execution" of the tasks and its subtasks. Unlike some frameworks which differentiates between *agents* and *tools*, **AgentOrg** combines both into an *Agent* component. Responsible for the execution and managed by the orchestrator, each Agent are designed to convert instructions into results. Although structured, *Agents* can be designed to do high level complicated tasks and can call other agents itself, greatly enhancing its ability to address. 

# Implementation
:::tip  Technical Details
Each Agent represent a group of GraphNodes on a LangGraph and can be subgraphed.
:::

BaseAgent is the parent class of all agents is the BaseAgent and consists of a `description` attribute and `execute()` abstract method.

### Attributes
#### Description
`description` is a string that describes the task that the BaseAgent is meant to handle. This is used by the Generator to assign the right task for the agent when generating the TaskGraph.

Some examples:
    - "The agent that used to deliver the message to the user, either a question or provide some information." ([MessageAgent](./MessageAgent.md))
    - ""Answer the user's questions based on the company's internal documentations (unstructured text data), such as the policies, FAQs, and product information" ([RAGAgent](./RAGAgent.md))

#### Execute
`execute()` takes in [MessageState](../MessageState.md) and returns an `invoke`'d LangChain StateGraph. This is crucial to connect various Agents (through LangChain subgraph behavior) and is called by the Orchestrator during runtime.

An example:
```py
def execute(self, msg_state: MessageState):
    graph = self.action_graph.compile()
    result = graph.invoke(msg_state)
    return result
```

### Code
```py
class BaseAgent(ABC):
    
    description = None

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"
    
    @abstractmethod
    def execute(self, msg_state: MessageState):
        pass
```
