import tiktoken

def chunk_string(text, tokenizer, max_length, from_end=True):
    # Initialize the tokenizer
	encoding = tiktoken.get_encoding(tokenizer)
	tokens = encoding.encode(text)
	if from_end:
		chunks = encoding.decode(tokens[-max_length:])
	else:
		chunks = encoding.decode(tokens[:max_length])
	return chunks