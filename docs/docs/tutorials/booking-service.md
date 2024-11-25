---
sidebar_position: 6
---

# Booking Service Bot

*Connect your bots to databases through DatabaseAgents*

## Intro

In this tutorial, we'll walk through building a simple booking service bot using **AgentOrg**'s framework. This bot will be able to handle common customer inquiries, such as find room availabilities, booking rooms, retrieve booking details, and modifying or cancelling existing bookings. The tutorial aims to provide a next step up from [simple Q&A conversational AIs](./customer-service.md) to a powerful bot that can integrate directly with databases and tools used in many workplaces.

By the end of this tutorial, you'll know how to use external tooling agents specifically integrating with a database. This tutorial demonstrates non-chat related agents and serves as an entry into deeper and more complex capabilities.


## Setting up the Config File

[Previously](./customer-service.md), we had nodes that were able to read from various files and sources to compose an answer. Here, we will take it a step further. Instead of just reading, we will also be interacting with database and writing record into database. This could be done through the built-in [DatabaseAgent](../Agents/DatabaseAgent.md).

Here is the really simple structure for a *Config* JSON file:

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

Now, lets see it with the Booking Assistant Service Bot example. Here, we have a sample Config file of a Customer Service Bot for a robotics cleaning company RichTech.

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
    "rag_docs": [{
        "source": "https://irishrep.org/",
        "num": 30
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

 to create the TaskGraph! TaskGraphs is the graph that the bot traverses through, so it does not have to take time and update every time the user runs it. With the bot running on top of TaskGraphs, you would only need to re-generate the TaskGraph any time you update the graph!

## Running the Bot

With the TaskGraph in place, we can run the bot on the TaskGraph with 

`python run.py --input-dir ./examples/booking_system`

With that in place, that should be all you need!

---

## Sample Conversation

```
Bot: Hello! I'm your Booking Assistant. Looking to book tickets for a show? I can provide information on events, venues, and ticket availability, and help you with the booking process. Need recommendations? Just let me know your preferences!

User: hat are the current shows running?

Bot: It looks like there is a show currently running with the following schedule:

- Wednesday: 3pm & 8pm
- Thursday: 7pm
- Friday: 8pm
- Saturday: 3pm & 8pm
- Sunday: 3pm

The show has a running time of 70 minutes with no intermission, and it uses haze and smoke effects. If you need more information or assistance with booking, feel free to ask!

User: What is the name of that show?

Bot: The name of the show currently running with the provided schedule is not explicitly mentioned in the context provided. However, based on the information about the cast and creative team, it appears to be the show featuring Brutus Jones played by Obi Abili. If you have any more questions or need assistance, feel free to ask!

User: what is the name of the show running at Wednesday 3pm?

Bot: The name of the show running at Wednesday 3pm is "The Emperor Jones," featuring Brutus Jones played by Obi Abili. If you need more information or assistance with booking, feel free to ask!

User: What is the name of the show running at Thursday 7pm?

Bot: The name of the show running at Thursday 7pm is "The Emperor Jones," featuring Brutus Jones played by Obi Abili. If you need more information or assistance with booking, feel free to ask!

User: Are there space left for the Thursday 7PM show?

== freezes ==
```

```
Bot: Hello! I'm your Booking Assistant. Looking to book tickets for a show? I can provide information on events, venues, and ticket availability, and help you with the booking process. Need recommendations? Just let me know your preferences!

User: Can you tell me about the shows currently?

Bot: Currently, there are several shows and performances available. Here are some highlights:

1. **Only Murders in the Building** - You can currently catch this show, which is part of a series featuring notable performances.

2. **Holiday Schedule Performances** - There are special holiday schedules with additional performances on certain dates. For instance, there will be performances on Monday, December 19 at 7pm, Tuesday, December 20 at 2pm and 7pm, and additional shows on Tuesday, December 27 at 7pm, and Friday, December 30 with a matinee at 2pm and an evening show at 7pm.

3. **Special Events** - There are special events like the $22 on 22nd On-Sale, which started on November 17, 2022, at 1pm, and an Opening Night event on December 8, 2022, at 7pm.

If you have specific preferences or need more information about a particular show, feel free to ask!

User: What are the availability for "Only Murders in the Building"?

Bot: Currently, I don't have specific information on the ticket availability for "Only Murders in the Building." However, you can purchase tickets through the Irish Repertory Theatre website or by calling the box office at (212) 727-2737. If you have any preferences or need further assistance with the booking process, feel free to ask!

User: What is the next show? 

Bot: The next show mentioned in the context is the American Premiere of "After Luke," which is part of the Irish Repertory Theatre's 2008-2009 season. Would you like more information about this show or any other assistance?

User: I want to watch a show right now, what is the next show I could book?

Bot: Could you let me know what type of event you're interested in, as well as your preferred date and location?

User: What type of events are there? my schedule is flexible so date and location doesn't matter

Bot: Could you share your preferences regarding the type of event, location, or any particular interests you have?

User: What type of events are there? I am open to any event, location, or interests

Bot: Here's a list of events that align with your preferences. Let me know if any of these catch your interest.

User: Nothing was shown?

Bot: Is there a particular event you want more details about, or would you like me to provide additional options?

**user quits**
```