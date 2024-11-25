---
sidebar_position: 6
---

# Customer Service Bot

*Enhance your bots with RAG through RAGMsgAgents*

## Intro

In this tutorial, we'll walk through building a basic customer service bot using **AgentOrg**'s framework. This bot will be able to handle common customer inquiries, such as answering FAQs, identifying customer preferences, and retrieve relevant contact information. The tutorial aims to build on top of a [simple conversational AI](./roleplay-chatbot.md) to include RAG and information retrieval in order to equip you with the foundational skills needed to create and deploy a functional customer service bot.

By the end of this tutorial, you'll know how to set up the AI framework, supply RAG-able data, build a basic conversation flow, and power a bot with it. Whether you're building your first bot or refining your skills, this tutorial will guide you in creating a responsive and helpful customer service chatbot. 

## Supplying Information

Before any technical work is done, we must first identify and find information to supply to the bot. After all, you can't serve as a Customer Support Agent without anything to support! To add resources to the bot, we need to decide what the bot should known and look for links to sources in which the bot can learn from. For this example, we will be using a companies' website to supply to the bot. Keep it saved somewhere, we will be needing it for our next step!

## Setting up the Config File

In its core, bot is powered through a *TaskGraph* which is the structure that links various tasks together to fulfill the overall role of the bot. Each "node" represents a task which has an *Agent* that is selected to complete task. Each node engages the user for their response, and  with the user response, the TaskGraph will decide which next node to travel to.

Like actual conversations, *TaskGraph* can be complicated; that is why we help you convert a simple and intuitive *Config* JSON file into a powerful and advanced *TaskGraph* through our generator. Instead of needing to design an entire graph, all you need to do is to describe the bot and provide some extra information and it will build the graph for you! 

#### Composite Agents
Building on top of a primitive conversational bot, for the customer service bot, we need to let the bot be able to read from the data we are supplying when composing a response. We can do that is through the [RAGMsgAgent (RAG-Message Agent)](../Agents/RAGAgent.md). The RAGMsgAgent is different than some of the agents we used in the previous tutorial because it is a *composite* agent. Inside RAGMsgAgent is actually two other agents, [RAGAgent](../Agents/RAGAgent.md) and [MessageAgent](../Agents/MessageAgent.md). When we call RAGMsgAgent, it internally calls RAGAgent which retrieves the relevant information from our sources and then passes the information to MessageAgent which composes the response which the RAGMsgAgent outputs. While RAGMsgAgent is pretty simple, there is no limit to how complex such composite agents could be and this serves as a sneak peak to what is ahead to come.

As a refresher, here is the simple structure for a [Config](../Config.md) JSON file:

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

Now, lets see it with the Customer Service Bot example. Here, we have a sample Config file of a Customer Service Bot for a robotics cleaning company RichTech.

```json
{
    "role": "customer service assistant",
    "objective": [
        "Request customer contact information"
    ],
    "domain": "robotics and automation",
    "intro": "Richtech Robotics's headquarter is in Las Vegas; the other office is in Austin. Richtech Robotics provide worker robots (ADAM, ARM, ACE), delivery robots (Matradee, Matradee X, Matradee L, Richie), cleaning robots (DUST-E SX, DUST-E MX) and multipurpose robots (skylark). Their products are intended for business purposes, but not for home purpose; the ADAM robot is available for purchase and rental for multiple purposes. This robot bartender makes tea, coffee and cocktails. Richtech Robotics also operate the world's first robot milk tea shop, ClouTea, in Las Vegas (www.cloutea.com), where all milk tea beverages are prepared by the ADAM robot. The delivery time will be one month for the delivery robot, 2 weeks for standard ADAM, and two months for commercial cleaning robot. ",
    "docs": {
        "source": "https://www.richtechrobotics.com/",
        "num": 20
    },
    "tasks": [],
    "agents": [
        "RAGAgent",
        "RagMsgAgent",
        "MessageAgent",
        "SearchAgent",
        "DefaultAgent"
    ]
}
```

With our Config in place, the vast majority of work is surprisingly already done! The rest is simply bringing the bot to life.

## Generating a TaskGraph

Now that we have a Config file, generating the graph is the easy part. All you need to do is run 

`python create.py --config ./examples/customer_service_config.json --output-dir ./examples/customer_service`

 to create the TaskGraph! TaskGraphs is the graph that the bot traverses through, so it does not have to take time and update every time the user runs it. With the bot running on top of TaskGraphs, you would only need to re-generate the TaskGraph any time you update the graph!

## Running the Bot

With the TaskGraph in place, we can run the bot on the TaskGraph with 

`python run.py --input-dir ./examples/customer_service`

With that in place, that should be all you need!

---

## Sample Conversation
