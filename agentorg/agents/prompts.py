## TODO: refactor message/rag/rag_prompts.py to use these prompts
message_generator_prompt = """Based on the conversation history between a User and Assistant, please paraphrase the following message to the user [Notice: add information of the initial response which is helpful to respond to the user if any].
Conversation:
{formatted_chat}

Initial Response:
{initial_response}

Message:
{message}
"""


context_generator_prompt = """Refer to the provided context to answer the user's question. The response should be based on the conversation history. Respond like daily chat.
Conversation:
{formatted_chat}

Question: {question}

Context: {context}
"""


generator_prompt = """Answer the user's question based on the conversation history. Respond like daily chat.
Conversation:
{formatted_chat}

Question: {question}
"""


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


database_action_prompt = """You are an assistant that has access to the following set of actions. Here are the names and descriptions for each action:
{actions_info}
Based on the conversation history and the user's message, please provide the action that the user is intened to take.
Conversation:
{formatted_chat}
User's Message:
{message}
The response must be the name of one of the actions ({actions_name}).
"""