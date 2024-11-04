# RAG Agent

In order to use the RAG agent, please follow steps below:

- Open the `load_documents.py` file under the `tools/RAG` folder and set up URLs to crawl (TODO: support other crawling functions).
- Run the `load_documents.py` file to create and save the crawled content in a folder.
- Open the `utils.py` file under the `tools/RAG` folder and find the `RetrieverEngine` class. Change the database path in that class as the folder path which saves the crawled content
- Open `AgentOrg/agentorg/orchestrator/examples/default_taskgraph.json` and change the agent name of an appropriate node to "RAGAgent".