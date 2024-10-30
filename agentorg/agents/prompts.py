message_generator_prompt = """Based on the conversation history between a User and Assistant, please paraphrase the following message to the user [Notice: refer to the information of the initial response if any].
Conversation:
{formatted_chat}

Initial Response:
{initial_response}

Message:
{message}
"""

"message_flow"

rag_generator_prompt = """Refer to the provided context to answer the user's question. The response should be based on the conversation history. Respond like daily chat.
Conversation:
{formatted_chat}

Question: {question}

Context: {context}
"""

retrieve_contextualize_q_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is. \
        {chat_history}"""