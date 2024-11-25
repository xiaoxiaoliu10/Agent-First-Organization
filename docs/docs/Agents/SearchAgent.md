# SearchAgent

## Introduction

Search Agents retrieve real-time data from the web or databases, and generate coherent and user-specific responses. The searched results enable them to address complex and time-sensitive queries effectively by integrating up-to-date information with their foundational knowledge.

## Tavily API Integration

You can get an API key by visiting [this site](https://python.langchain.com/docs/integrations/tools/tavily_search/#:~:text=key%20by%20visiting-,this%20site,-and%20creating%20an) and creating an account.

## Samlpe Conversation

```json title="searchagent_function_sample.json"
Bot: Hello! How can I help you today?
You: I want to know the latest gaming result of Formula 1.
Bot: The latest gaming result from Formula 1 is that Charles Leclerc won the United States Grand Prix, with Ferrari achieving a one-two finish. Max Verstappen finished behind the Ferrari drivers.
```

You can checkout the [LangSmith Trace](https://smith.langchain.com/public/f55696d8-310d-4060-a90c-d6fae0b6a254/r) for the execution process. The Search Agent first searches online resources relevant to the user's query and then generates the final response.



