# Booking Service Bot

*Connect your bots to databases through DatabaseAgents*

## Intro

In this tutorial, we'll walk through building a booking performance bot using **AgentOrg**'s framework. This bot will be able to handle common customer inquiries, such as find show's availabilities, booking shows, retrieve performance schedule, and modifying or cancelling existing bookings. The tutorial aims to provide a next step up from [simple Q&A conversational AIs](./customer-service.md) to a powerful bot that can integrate directly with databases and tools used in many workplaces.

By the end of this tutorial, you'll know how to use external tooling agents specifically integrating with a database. This tutorial demonstrates a agent served as an entry into deeper and more complex capabilities.


## Setting up the Config File

[Previously](./customer-service.md), we had nodes that were able to read from various files and sources to compose an answer. Here, we will take it a step further. Instead of just reading, we will also be interacting with database and writing record into database. This could be done through the built-in [DatabaseAgent](../Agents/DatabaseAgent.md).

As a refresher, here is the structure for a *Config* JSON file:

* `role (Required)`: The general "role" of the chatbot you want to create. For instance, "customer service assistant", "data analyst", "shopping assistant", etc.
* `user_objective (Required)`: The user's goal that the chatbot wants to achieve. Related to the user experience. Description in third person. For instance, "The customer service assistant helps users with customer service inquiries. It can provide information about products, services, and policies, as well as help users resolve issues and complete transactions."
* `builder_objective (Optional)`: The additional target you want the chatbot to achieve beyond the user's goal. Can contain hidden objectives or subtle objectives which is hidden from the user. Describe in third person. For instance, "The customer service assistant helps to request customer's contact information."
* `domain (Optional)`: The domain that you want to create the chatbot for. For instance, "robotics and automation", "Ecommerce", "Healthcare", etc.
* `intro (Optional)`: The introduction of the above domain that you want to create the chatbot for. It should contain the information about the domain, the products, services, and policies, etc.
* `task_docs (Optional, List[Dict])`: The documents resources for the taskgraph generation to create the chatbot. Each item in the list should contain the following fields:
    * `source (Required)`: The source url that you want the chatbot to refer to
    * `desc (Optional)` : Short description of the source and how it is used
    * `num (Optional)`: The number of websites that you want the chatbot to refer to for the source, defaults to one (only the url page)
* `rag_docs (Optional, List[Dict])`: If you want to use RAGAgent, then here indicates the documents for the RAG component of chatbot when running chatbot. Each item in the list should contain the following fields:
    * `source (Required)`: The source url that you want the chatbot to refer to
    * `desc (Optional)` : Short description of the source and how it is used
    * `num (Optional)`: The number of websites that you want the chatbot to refer to for the source, defaults to one (only the url page)
* `tasks (Optional, List(Dict))`: The pre-defined list of tasks that the chatbot need to handle. If empty, the system will generate the tasks and the steps to complete the tasks based on the role, objective, domain, intro and docs fields. The more information you provide in the fields, the more accurate the tasks and steps will be generated. If you provide the tasks, it should contain the following fields:
    * `task_name (Required, Str)`: The task that the chatbot need to handle
    * `steps (Required, List(Str))`: The steps to complete the task
* `agents (Required, List(AgentClassName))`: The [Agents](Agents/Agents.md) pre-defined under `agentorg/agents` folder in the codebase that you want to use for the chatbot.

Now, lets see it with the Booking Assistant example. Here, we have a sample Config file of a Booking Assistant for a performance company - The Irish Repertory Theatre.

```json
{
    "role": "booking assistant",
    "user_objective": "The booking assistant helps users book tickets for the show. It can provide information about events, venues, and ticket availability, as well as help users complete the booking process. It can also provide recommendations based on user preferences.",
    "builder_objective": "The booking assistant ask for user feedback at the end of the conversation.",
    "domain": "Theatre",
    "intro": "The mission of Irish Repertory Theatre is to provide a context for understanding the contemporary Irish-American experience through evocative works of theater, music, and dance. This mission is accomplished by staging the works of Irish and Irish-American classic and contemporary playwrights, encouraging the development of new works focused on the Irish and Irish-American experience, and producing the works of other cultures interpreted through the lens of an Irish sensibility.",
    "task_docs": [{
        "source": "https://irishrep.org/",
        "num": 10
    }],
    "tasks": [],
    "agents": [
        "MessageAgent",
        "DatabaseAgent",
        "DefaultAgent"
    ]
}
```
With our Config in place, the vast majority of work is surprisingly already done! The rest is simply bringing the bot to life.

## Generating a TaskGraph

Now that we have a Config file, generating the graph is the easy part. All you need to do is run 

`python create.py --config ./examples/booking_assistant_config.json --output-dir ./examples/booking_system`

It will first enter into a *task planning* interactive panel where you can see the generated tasks this bot will handle and the following steps to complete the specific tasks. You can also modify the tasks and steps as needed. Once you are satisfied with result, you could press `s` to save the *task planning* file then it will further generate the final *TaskGraph* file. 

TaskGraph provides the graph that the bot will traverse through during the conversation. It provides a guideline for the conversation to make it more controllable and reliable. The details can be viewed at [here](../Taskgraph/Generation.md).

It will also prepare the database for the bot. The details can be viewed at [DatabaseAgent](../Agents/DatabaseAgent.md).
>**Notice**: The database content we used in this tutorial is a fake database for demonstration purposes. You can replace it with your own database content.

## Running the Bot

With the TaskGraph in place, we can run the bot on the TaskGraph with 

`python run.py --input-dir ./examples/booking_system`

It will initialize the service (e.g. NLU apis) you need to start the bot and you can start interacting with it!

---

## Evaluation
For a task-oriented dialogue system, you could use the evaluation script to automatically generate synthetic conversations, extracting task completion metrics for evaluating the whole system. For more details, please refer to the [evaluation](../Evaluation/UserSimulator.md) documentation.
1. First, create an API for the Agent you built. It will start an API on the default port 8000.
    ```
    python model_api.py  --input-dir ./examples/booking_system
    ```

2. Then, start the evaluation process:
   ```
    python eval.py \
    --model_api http://127.0.0.1:8000/eval/chat \
    --config ./examples/booking_assistant_config.json \
    --documents_dir ./examples/booking_system \
    --output-dir ./examples/booking_system
    ```

## Evaluation Results
The evaluation will generate the following outputs in the specified output directory:
1. **Simulated Synthetic Dataset (`simulate_data.json`)**  
   - JSON file containing simulated conversations generated based on the user's objective to evaluate the task success rate.
  
2. **Labeled Synthetic Dataset (`labeled_data.json`)**  
   - JSON file containing labeled conversations generated based on the taskgraph to evaluate the NLU performance.

3. **Goal Completion Metrics (`goal_completion.json`)**  
   - JSON file summarizing task completion statistics based on the bot's ability to achieve specified goals.