import inspect
from agentorg.utils.graph_state import MessageState, ConvoMessage
from agentorg.orchestrator.NLU.nlu import NLU, SlotFilling

TOOL_REGISTRY = {}

    
def register_tool(desc, slots=[], outputs=[]):
    def inner(func):
        """Decorator to register a worker."""
        TOOL_REGISTRY[f':{func.__name__}'] = Tool(func, desc, slots, outputs)

        return func
    return inner

class Tool:
    def __init__(self, func, description, slots, outputs):
        self.func = func
        self.description = description
        self.slots = slots
        self.output = outputs
        self.slotFill: SlotFilling = None
        
    def initSlotFill(self, slotFill: SlotFilling):
        self.slotFill = slotFill
        
    def preprocess(self, state: MessageState):
        ## preprocess
        if not self.slots:
            return self.func(state)
        
        if not self.slotFill:
            raise Exception("slotfill not instantiated")
        
        # slotfill API
        pred_slots = self.slotFill.execute(
            state.user_message.message, 
            self.slots, 
            state.user_message.history
        )
        
        params = [pred_slots[p] for p in inspect.signature(self.func).keys() if p in pred_slots]
        return self.func(*params)

    def postprocess(self, result):
        pass
    
    def execute(self, state: MessageState) -> MessageState:
        result = self.preprocess(state)
            
        ## postprocess
        state.response = str(result)
        return result
        
        
        
    '''
    input msgstate --> output msgstate
    prev: input msgstate --> worker --> output msgstate
    goal: input msgstate --> tool --> output msgstate
    
    tool
    1. tool(state) -> state
    2. tool(**params) -> state
    3. tool(state) --> values { --> (context) generator --> msg.response }
    4. tool(**params) --> values
    
    cases:
    1. treat as worker
    2-4. add pre-exec and post-exec
    
    pre-exec:
        using slots to convert state -> params
    
    post-exec:
        challenge - no signature off of (as much) <for dictionary mapping>
        reverse-slot - hardcoded
    
    Worker to Tool
    worker(state, state) = tool(state): param -> tool(param): param -> tool(param): state
    worker(state, state) = tool(state): param -> state -> tool(state): param
    
    slotfilling todo:
    slotfilling (params)
    reverse-slotfilling
    
    ''' 
    
    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"
    