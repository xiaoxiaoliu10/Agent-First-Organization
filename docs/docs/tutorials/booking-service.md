---
sidebar_position: 6
---

# Booking Service Bot Tutorial

## Intro

In this tutorial, we'll walk through building a simple booking service bot using **Articulate.AI**'s framework. This bot will be able to handle common customer inquiries, such as find room availabilities, booking rooms, retrieve booking details, and modifying or cancelling existing bookings. The tutorial aims to provide a next step up from [simple Q&A conversational AIs](./customer-service.md) to a powerful bot that can integrate directly with databases and tools used in many workplaces.

By the end of this tutorial, you'll know how to use non-conversational tooling agents, and integrate with a database. Whether you're building your first bot or refining your skills, this tutorial will guide you in creating a responsive and helpful customer service chatbot. 

## Building our Database

For this tutorial, in order to demonstrate how we can have tooling agents manipulate databases, we need to have a database first so it can operate on it. As this is not a guide on databases, we won't go into much details but for the purposes of this tutorial, we will be using a MySQL database built from this schema below!

```sql
test
```

## Setting up the Config File

[Previously](./customer-support.md), we had nodes that were able to read from various files and sources to compose an answer. Here, we will take it a step further. Instead of just reading, we will also be writing. This could be done through 

Here is the really simple structure for a *Config* JSON file:

* `role (Required)`: The general "role" of the chatbot you want to create
* `objective (Optional)`: The objective of the chatbot. This is like the "goal" or "target" you want your chatbot to fulfill or achieve while serving in its role.
* `domain (Optional)`: The domain of the company that you want to create the chatbot for
* `intro (Required)`: The introduction of the company that you want to create the chatbot for or the summary of the tasks that the chatbot need to handle
* `docs (Optional, Dict)`: The documents resources for the chatbot. The dictionary should contain the following fields:
    * `source (Required)`: The source url that you want the chatbot to refer to
    * `num (Required)`: The number of websites that you want the chatbot to refer to for the source
* `tasks (Optional, List(Dict))`: The pre-defined list of tasks that the chatbot need to handle. If empty, the system will generate the tasks and the steps to complete the tasks based on the role, objective, domain, intro and docs fields. The more information you provide in the fields, the more accurate the tasks and steps will be generated. If you provide the tasks, it should contain the following fields:
    * `task_name (Required, Str)`: The task that the chatbot need to handle
    * `steps (Required, List(Str))`: The steps to complete the task
* `agents (Required, List(AgentClassName))`: The agents pre-defined under agentorg/agents folder that you want to use for the chatbot. 

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

`python script.py --type novice --config <config-filepath>`

 to create the TaskGraph! TaskGraphs is the graph that the bot traverses through, so it does not have to take time and update every time the user runs it. With the bot running on top of TaskGraphs, you would only need to re-generate the TaskGraph any time you update the graph!

## Running the Bot

With the TaskGraph in place, we can run the bot on the TaskGraph with 

`python script.py --type apprentice --config-taskgraph <taskgraph-filepath>`

With that in place, that should be all you need!

---

## Sample Conversation

> INSERT SAMPLE HERE