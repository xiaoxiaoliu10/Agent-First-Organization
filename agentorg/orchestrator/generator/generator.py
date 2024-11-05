import json
import logging
from datetime import datetime
from tqdm import tqdm as progress_bar

from langchain.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from agentorg.utils.utils import postprocess_json
from agentorg.orchestrator.generator.prompts import *
from agentorg.orchestrator.generator.loader import Loader
import agentorg.agents
from agentorg.agents.agent import AGENT_REGISTRY


logger = logging.getLogger(__name__)


class Generator:
    def __init__(self, config, model):
        self.product_kwargs = json.load(open(config))
        self.type = self.product_kwargs.get("type")
        self.objective = self.product_kwargs.get("objective")
        self.intro = self.product_kwargs.get("intro")
        self.docs = self.product_kwargs.get("docs")
        self.tasks = self.product_kwargs.get("tasks")
        self.agents = self.product_kwargs.get("agents")
        self.model = model
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.orche_config_filepath = f"./agentorg/orchestrator/examples/{self.type}_taskgraph_{timestamp}.json"
    

    def _generate_tasks(self):
        # based on the type and documents
        prompt = PromptTemplate.from_template(generate_tasks_sys_prompt)
        input_prompt = prompt.invoke({"type": self.type, "intro": self.intro, "docs": self.documents})
        final_chain = self.model | StrOutputParser()
        answer = final_chain.invoke(input_prompt)
        logger.debug(f"Generated tasks with thought: {answer}")
        self.tasks = postprocess_json(answer)

    def _format_tasks(self):
        # TODO: need to use LLM to match the semantics meaning of the tasks
        new_format_tasks = []
        for task_str in self.tasks:
            task = {}
            task['intent'] = task_str
            task['task'] = task_str
            new_format_tasks.append(task)
        self.tasks = new_format_tasks

    def _generate_best_practice(self, task):
        # based on the task
        prompt = PromptTemplate.from_template(generate_best_practice_sys_prompt)
        input_prompt = prompt.invoke({"task": task})
        final_chain = self.model | StrOutputParser()
        answer = final_chain.invoke(input_prompt)
        logger.debug(f"Generated best practice with thought: {answer}")
        return postprocess_json(answer)
    
    def _finetune_best_practice(self, best_practice):
        # based on the best practice
        prompt = PromptTemplate.from_template(finetune_best_practice_sys_prompt)
        resources = {}
        for agent_name in self.agents:
            agent_desp = AGENT_REGISTRY.get(agent_name).description
            resources[agent_name] = agent_desp
        input_prompt = prompt.invoke({"best_practice": best_practice, "resources": resources, "objectives": self.objective})
        final_chain = self.model | StrOutputParser()
        answer = final_chain.invoke(input_prompt)
        return postprocess_json(answer)

    def generate(self):
        # Step 0: Load the docs
        if self.docs:
            source = self.docs.get("source")
            num_docs = self.docs.get("num")
            loader = Loader(source, num_docs)
            crawled_docs = loader.load()
            logger.debug(f"Loaded {len(crawled_docs)} documents")
            self.documents = "\n\n".join([doc['url'] + "\n" + doc["content"] for doc in crawled_docs])
        else:
            self.documents = ""

        # Step 1: Generate the tasks
        if not self.tasks:
            self._generate_tasks()
            logger.info(f"Generated tasks: {self.tasks}")
        else:
            self._format_tasks()
            logger.info(f"Formatted tasks: {self.tasks}")

        # Step 2: Generate the task graph
        best_practices = []
        for idx, task in progress_bar(enumerate(self.tasks), total=len(self.tasks)):
            logger.info(f"Generating best practice for task {idx}: {task}")
            best_practice = self._generate_best_practice(task)
            logger.info(f"Generated best practice for task {idx}: {best_practice}")
            finetuned_best_practice = self._finetune_best_practice(best_practice)
            logger.info(f"Finetuned best practice for task {idx}: {finetuned_best_practice}")
            best_practices.append(finetuned_best_practice)

        node_id = 1
        nodes = []
        edges = []
        task_ids = {}
        for best_practice, task in zip(best_practices, self.tasks):
            task_ids[node_id] = task
            for idx, step in enumerate(best_practice):
                node = []
                node.append(str(node_id))
                node.append({
                    "name": step["resource"],
                    "attribute": {
                        "value": step['example_response'],
                        "task": step['task'],
                        "directed": False
                    },
                    "limit": 1
                })
                nodes.append(node)

                if idx == 0:
                    edge = []
                    edge.append("0")
                    edge.append(str(node_id))
                    edge.append({
                        "intent": task['intent'],
                        "attribute": {
                            "weight": 1,
                            "pred": True,
                            "definition": "",
                            "sample_utterances": []
                        }
                    })
                else:
                    edge = []
                    edge.append(str(node_id - 1))
                    edge.append(str(node_id))
                    edge.append({
                        "intent": "None",
                        "attribute": {
                            "weight": 1,
                            "pred": False,
                            "definition": "",
                            "sample_utterances": []
                        }
                    })
                edges.append(edge)
                node_id += 1
        
        # Add the start node
        start_node = []
        start_node.append("0")
        start_node.append({
            "name": "MessageAgent",
            "attribute": {
                "value": "Hello! How can I help you today?",
                "task": "Greetings",
                "directed": False
            },
            "limit": 1,
            "type": "start"
        })
        nodes.insert(0, start_node)

        task_graph = {
            "nodes": nodes,
            "edges": edges
        }

        with open(self.orche_config_filepath, "w") as f:
            json.dump(task_graph, f, indent=4)

        return self.orche_config_filepath