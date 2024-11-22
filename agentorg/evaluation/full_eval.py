import json
import argparse
from simulate_first_pass_convos import simulate_conversations
from extract_conversation_info import extract_task_completion_metrics
from simulate_second_pass_convos import get_labeled_convos

def evaluate(config):
    model_api = config['model_api']
    model_params = config['model_params']
    synthetic_data_params = config['synthetic_data_params']
    
    # first pass
    first_pass_data = simulate_conversations(model_api, model_params, synthetic_data_params, config)

    # extract items from first pass data
    bot_goal = config['builder_objective'][0]
    goal_metrics = extract_task_completion_metrics(first_pass_data, bot_goal)

    # second pass
    labeled_convos = get_labeled_convos(first_pass_data, model_api, synthetic_data_params, model_params, config)
    return labeled_convos, goal_metrics

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--model_api', type=str, default="http://adaptation.cs.columbia.edu:55231/qa/richtech/v1alpha1")
    parser.add_argument('--model_params', type=dict, default={})
    parser.add_argument('--num_convos', type=str, default=2)
    parser.add_argument('--num_goals', type=str, default=2)
    parser.add_argument('--max_turns', type=str, default=6)
    parser.add_argument('--documents_dir', type=str, default='/local2/rs4235/AgentOrg/agentorg/evaluation/temp_files')
    parser.add_argument('--config', type=str, default="./temp_files/richtech_config.json")
    args = parser.parse_args()

    assert args.model_api is not None, "Model api must be provided"
    assert args.config is not None, "Config file must be provided"

    config = json.load(open(args.config))
    config['model_api'] = args.model_api
    config['documents_dir'] = args.documents_dir
    config['model_params'] = args.model_params
    config['synthetic_data_params'] = {'num_convos': args.num_convos, 'num_goals': args.num_goals, 
                                       'max_turns': args.max_turns}

    final_convos, goal_metrics = evaluate(config)

    with open('labeled_data.json', 'w') as f:
        json.dump(final_convos, f, indent=5)
    
    with open('goal_completion.json', 'w') as f:
        json.dump(goal_metrics, f, indent=5)