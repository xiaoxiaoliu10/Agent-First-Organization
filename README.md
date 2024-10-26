## How to start?
1. Install the dependencies by running `pip install -r requirements.txt`
2. Run the NLU server by running `fastapi dev agentorg/orchestrator/NLU/api.py --port 55134 --host 0.0.0.0`
3. Update the "nluapi" value in the `agentorg/orchestrator/examples/default.json` config file.
4. Run the script: `python script.py`