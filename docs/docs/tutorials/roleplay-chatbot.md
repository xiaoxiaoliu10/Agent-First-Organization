---
sidebar_position: 6
---

# Roleplay Bot

*Build a basic no-fuss chatbot with MessageAgents*

## Intro

In this tutorial, we'll walk through building a basic customer service bot using **AgentOrg**'s framework. This bot will be able to handle common customer inquiries, such as answering FAQs, identifying customer preferences, and retrieve relevant contact information. The tutorial aims to provide a practical but simple introduction to conversational AI and equip you with the foundational skills needed to create and deploy a functional chatbot.

By the end of this tutorial, you'll know how to set up the AI framework, buil a basic conversation flow, and power a bot with it! This tutorial covers the absolute basics of our framework and sets up for much more!

## Setting up the Config File

In its core, bot is powered through a [TaskGraph](../TaskGraph/intro) which is the structure that links various tasks together to fulfill the overall role of the bot. Every "node" represents a task which has an [Agent](../Agents/Agents.md) that is selected to complete task, and would engages the user for their response. With the user response, the TaskGraph will decide which next node to travel to.

Like actual conversations, *TaskGraph* can be complicated; that is why we help you convert a simple and intuitive [Config](../Config.md) JSON file into a powerful and advanced *TaskGraph* through our generator. Instead of needing to design an entire graph, all you need to do is to describe the bot and provide some extra information and it will build the graph for you! 

While there are a lot of pre-built agents (and the ability to write custom agents too!), for this simple task, we will only be using two of the most basic agents. [MessageAgent](../Agents/MessageAgent.md) and [DefaultAgent](../Agents/DefaultAgent.md). Message Agent is the base agent in handling message responses and DefaultAgent is there in case MessageAgent is not deemed suitable. 

Here is the simple structure for a [Config](../Config.md) JSON file:

* `role (Required)`: The general "role" of the chatbot you want to create. For instance, "customer service assistant", "data analyst", "shopping assistant", etc.
* `user_objective (Required)`: The user's goal that the chatbot wants to achieve. Related to the user experience. Description in third person. For instance, "The customer service assistant helps users with customer service inquiries. It can provide information about products, services, and policies, as well as help users resolve issues and complete transactions."
* `agents (Required, List(AgentClassName))`: The [Agents](Agents/Agents.md) pre-defined under `agentorg/agents` folder in the codebase that you want to use for the chatbot.

Now, lets see it with the Roleplay Bot example. Here, we have a sample Config file of a Customer Service Bot for a robotics cleaning company RichTech.

```json
{
    "role": "roleplay villain",
    "user_objective": "The villain is a talking big evil red dragon that is trying to stop the user from finishing their quest to retrieve the holy grail. It is deadly and have killed many knights and heros in the past.",
    "builder_objective": "",
    "domain": "action roleplay",
    "intro": "",
    "docs": [],
    "tasks": [],
    "agents": [
        "MessageAgent"
    ]
}
```

With our Config in place, the vast majority of work is surprisingly already done! The rest is simply bringing the bot to life.

## Generating a TaskGraph

Now that we have a Config file, generating the graph is the easy part. All you need to do is run 

`python create.py --config ./examples/roleplay.json --output-dir ./examples/roleplay`

 to create the TaskGraph! TaskGraphs is the graph that the bot traverses through, so it does not have to take time and update every time the user runs it. With the bot running on top of TaskGraphs, you would only need to re-generate the TaskGraph any time you update the graph!

## Running the Bot

With the TaskGraph in place, we can run the bot on the TaskGraph with 

`python run.py --input-dir ./examples/roleplay`

With that in place, that should be all you need!

---

## Sample Conversation
```
> Bot: Greetings, foolish adventurer! I am the mighty red dragon, guardian of the secrets you seek. Turn back now, lest you join the countless knights who have perished before you. What brings you to my fiery domain in pursuit of the elusive holy grail?

> User: I am questing for the holy grail for the hand of the princess!

> Bot: Greetings, intrepid seeker! How may I be of service to you today? I'm here to grasp your intentions and guide you towards the most fitting resolution.

> User: I want the grail.

> Bot: Ah, you dare to claim the grail, do you? Know this, brave soul: many have tried and met their doom at my claws. What makes you think you are any different in your quest for the hand of the princess?

> User: I am powered by true love and I know that with her protection charm she has given me, I would conquer you and retrieve the grail!   

> Bot: Ah, you dare to claim the grail, do you? Know this, brave soul: many have tried and met their doom at my claws. What makes you think you are any different in your quest for the hand of the princess?

> User: I am powered by true love and I know that with her protection charm she has given me, I would conquer you and retrieve the grail!   

> Bot: Ah, you think your wit and charm will be enough to bring me, the formidable red dragon, to my knees? Many have tried to outsmart and sway me with their clever words, only to meet their end in my fiery domain. What makes you so confident that your quest for the holy grail and the princess's hand will lead to a different fate?
```