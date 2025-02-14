import json
import random
from agentorg.evaluation.build_user_profiles import build_profile
from agentorg.evaluation.chatgpt_utils import (chatgpt_chatbot, query_chatbot, filter_convo, adjust_goal,
                                               flip_hist, generate_goals, format_chat_history_str, flip_hist_content_only)


def check_goal_completion(goal, convo):
    convo_str = format_chat_history_str(flip_hist_content_only(convo[2:]))
    prompt = f"Here is a conversation between a user and a customer service chatbot assistant:\n{convo_str}\n\nThe user's goal is the following: {goal}\nOutput False if the user needs to learn more information regarding their goal. Output True otherwise. Only onput True or False and nothing else."
    output = chatgpt_chatbot([{'role': 'user', 'content': prompt}])
    return output == "True"

def conversation(model_api, profile, goal, summary, model_params, synthetic_data_params, env_config):
    history = []
    instructional_prompt = f'Pretend you are a human interacting with a customer service chatbot for the following company: {summary}\nYou have the following goal when interacting with this chatbot:\n{goal}\nHere is a description of the customer you are pretending to be:\n{profile}\nHave a conversation with the chatbot while trying to achieve your goal as this customer. Make sure the conversation is natural. For example, if the chatbot asks you a question you should answer it.'
    start_text = "Humans write short questions with occasional typos. Here are some examples of what a human customer would type: [how much is it?, Can you send info to my email, yes I need a job, want to check both proposals to rent and buy, How much does it cost a [PRODUCT_HERE], Im interested in [PRODUCT_HERE], hi i would like to rent out [PRODUCT_HERE] but im wondering which countries are available for rental]. Replicate the writing behavior of a human customer and begin the conversation with a question to achieve your goal."
    history.append({'role': 'system','content': instructional_prompt})
    history.append({'role': 'user', 'content': start_text})
    chatbot_history = []

    for i in range(synthetic_data_params['max_turns']):
        output = chatgpt_chatbot(history) 
        history.append({'role': 'assistant', 'content': output})
        chatbot_history.append({'role': 'assistant', 'content': output})
        response_data = query_chatbot(model_api, chatbot_history, model_params, env_config)
        answer = response_data["answer"]
        answer = answer.replace('\n', ' ')
        model_params = response_data["parameters"]
        pred_intent = response_data['parameters']['nlu_records'][-1]['pred_intent']
        history[-1]['intent'] = pred_intent

        history.append({'role': 'user', 'content': answer})
        chatbot_history.append({'role': 'user', 'content': answer})
        if i > 2 and check_goal_completion(goal, history.copy()):
            history.append({'goal_completetion': True})
            break
    
    if not history[-1].get('goal_completetion', False):
        history.append({'goal_completetion': False})
    history.append({'trajectory': model_params["history"]})
    return history

def generate_conversations(model_api, profiles, goals, summary, model_params, synthetic_data_params, env_config):
    convos = []
    for profile, goal in zip(profiles, goals):
        convo = conversation(model_api, profile, goal, summary, model_params, synthetic_data_params, env_config)
        convos.append(flip_hist(filter_convo(convo, filter_turns=False)))
    return convos

def simulate_conversations(model_api, model_params, synthetic_data_params, config):
    profiles, goals = build_profile(synthetic_data_params, config)
    summary = config['intro']
    env_config = {
        "workers": config['workers'],
        "tools": config["tools"]
    }
    
    try:
        conversations = generate_conversations(
            model_api,
            profiles,
            goals,
            summary,
            model_params,
            synthetic_data_params,
            env_config,
        )
    except Exception as e:
        print("Generate conversations failed")
        print("Error: ", e)
        conversations = []
    return conversations, goals

if __name__ == "__main__":
    model_api = "http://adaptation.cs.columbia.edu:55231/qa/richtech/v1alpha1"
    synthetic_data_params = {'num_convos': 5, 'num_goals': 3, 'max_turns': 10}
    model_params = {}
    convos  = simulate_conversations(model_api, model_params, synthetic_data_params)
    with open('p1_sample_convos.json', 'w') as f:
        json.dump(convos, f, indent=5)