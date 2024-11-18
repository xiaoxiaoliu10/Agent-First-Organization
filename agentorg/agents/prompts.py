### ================================== Generator Prompts ================================== ###
message_flow_generator_prompt = """{sys_instruct}\nBased on the conversation history between a User and Assistant, please paraphrase the following message to the user [Notice: add information of the initial response which is helpful to respond to the user if any].
Conversation:
{formatted_chat}

Initial Response:
{initial_response}

Message:
{message}
"""


message_generator_prompt = """{sys_instruct}\nBased on the conversation history between a User and Assistant, please paraphrase the following message to the user.
Conversation:
{formatted_chat}

Message:
{message}
"""


context_generator_prompt = """{sys_instruct}\nRefer to the provided context to answer the user's question. The response should be based on the conversation history.
Conversation:
{formatted_chat}

Question: {question}

Context: {context}
"""


generator_prompt = """{sys_instruct}\nAnswer the user's question based on the conversation history.
Conversation:
{formatted_chat}

Question: {question}
"""

### ================================== RAG Prompts ================================== ###

retrieve_contextualize_q_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is. \
        {chat_history}"""


choose_agent_prompt = """You are an assistant that has access to the following set of tools. Here are the names and descriptions for each tool:
{agents_info}
Based on the conversation history and user's message, choose the appropriate agent to respond to the user's message.
Conversation:
{formatted_chat}
User's Message:
{message}
The response must be the name of one of the agents ({agents_name}).
"""

### ================================== Database-related Prompts ================================== ###

database_action_prompt = """You are an assistant that has access to the following set of actions. Here are the names and descriptions for each action:
{actions_info}
Based on the given user intent, please provide the action that is supposed to be taken.
User's Intent:
{user_intent}
The response must be the name of one of the actions ({actions_name}).
"""


database_slot_prompt = """The user has provided a value for the slot {slot}. The value is {value}. 
If the provided value matches any of the following values: {value_list} (they may not be exactly the same and you can reformulate the value), please provide the reformulated value. Otherwise, respond None. 
Your response should only be the reformulated value or None.
"""
