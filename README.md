## How to start?
0. Set up environment
    * Add `OPENAI_API_KEY` and `LANGCHAIN_API_KEY` to `.env`
    * Set `LANGCHAIN_TRACING_V2` to `true` use `LangSmith` Trace [Optional]
1. Install the dependencies by running `pip install -r requirements.txt`
2. Build databases
    * Run `python -m agentorg.utils.loader --base_url="https://example.com" --folder_path="./agentorg/data" --get_chunk=True` to crawl web contents as the retriever database. For other args usage, please refer to `agentorg/utils/loader.py`.
    * Run `python -m agentorg.agents.tools.database.build_database --folder_path="./agentorg/data"` to load the sample SQLite database.
3. Create a config file, similar to the `project/AgentOrg/agentorg/orchestrator/examples/customer_service_config.json`
    * The config file should contain the following fields:
        * `role (Required)`: The general role of the chatbot you want to create
        * `user_objective (Required)`: The user's goal that you want the chatbot to achieve. Describe in third person.
        * `builder_objective (Optional)`: The additional target you want the chatbot to achieve beyond the user's goal. Describe in third person.
        * `domain (Optional)`: The domain of the company that you want to create the chatbot for
        * `intro (Required)`: The introduction of the company that you want to create the chatbot for or the summary of the tasks that the chatbot need to handle
        * `docs (Optional, Dict)`: The documentation of the chatbot. The dictionary should contain the following fields:
            * `source (Required)`: The source url that you want the chatbot to refer to
            * `num (Required)`: The number of websites that you want the chatbot to refer to for the source
        * `tasks (Optional, List(Dict))`: The pre-defined list of tasks that the chatbot need to handle. If empty, the system will generate the tasks and the steps to complete the tasks based on the role, objective, domain, intro and docs fields. The more information you provide in the fields, the more accurate the tasks and steps will be generated. If you provide the tasks, it should contain the following fields:
            * `task_name (Required, Str)`: The task that the chatbot need to handle
            * `steps (Required, List(Str))`: The steps to complete the task
        * `agents (Required, List(AgentClassName))`: The agents pre-defined under agentorg/agents folder that you want to use for the chatbot. Each agent will be defined as a class decorated with @register_agent. Please refer to the agentorg/agents/message_agent.py for an example.
4. Run the script: `python script.py --type novice --config <filepath of the above config>`
    * It will first generate a task plan based on the config file and you could modify it in an interactive way from the command line. Made the necessary changes and press `q` to save the task plan under `project/AgentOrg/agentorg/orchestrator/examples` folder and continue the task graph generation process.
    * Then it will generate the task graph based on the task plan and save it under `project/AgentOrg/agentorg/orchestrator/examples` folder.
    * Finally, it will automatically start the nluapi and slotapi services and start chat.
5. Next time, you could directly start to chat by skipping the task graph generation part: `python script.py --type apprentice --config-taskgraph <filepath of the above generated task graph file> `, which will directly load the task graph and start the chat (before running the script, execute `fastapi dev agentorg/orchestrator/NLU/api.py --port 55135 --host 0.0.0.0` to start NLU API).
6. You could also made changes directly to the task graph file. For example, train your own nlu model and slot model and start their apis. Then, update the corresponding path in the task graph config file. 