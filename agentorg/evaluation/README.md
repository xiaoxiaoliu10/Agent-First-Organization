# Task-Oriented Dialogue System Evaluation Script

This directory is designed to evaluate a task-oriented dialogue system by generating synthetic conversations, extracting task completion metrics, and producing a labeled synthetic dataset.

---

## **Inputs**

1. **Configuration File (`--config`)**  
   - A JSON configuration for the bot.
   - Example path: `files/richtech_config.json`.

2. **Model API (`--model_api`)**  
   - URL of the API endpoint for the dialogue model to be evaluated.  
   - Example: `http://myserver.com/chatbot`.

3. **Model Parameters (`--model_params`)**  
   - Dictionary containing any additional parameters for the dialogue model (optional).  
   - Example: `{}`.

4. **Synthetic Data Parameters**  
   These parameters control the generation of synthetic conversations:  
   - `--num_convos`: Number of synthetic conversations to simulate.  
   - `--num_goals`: Number of goals/tasks to simulate.  
   - `--max_turns`: Maximum number of turns per conversation.  

5. **Documents Directory (`--documents_dir`)**  
   - Path to the directory containing the relevant documents for the bot.
   - Example: `AgentOrg/agentorg/temp_files`.

---

## **Outputs**

1. **Labeled Synthetic Dataset (`labeled_data.json`)**  
   - JSON file containing labeled conversations generated during the evaluation process.

2. **Goal Completion Metrics (`goal_completion.json`)**  
   - JSON file summarizing task completion statistics based on the bot's ability to achieve specified goals.
