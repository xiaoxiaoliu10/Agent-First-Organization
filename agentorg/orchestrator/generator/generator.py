import json
import logging
from datetime import datetime
from tqdm import tqdm as progress_bar
import subprocess

from langchain.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from textual.app import App, ComposeResult
from textual.widgets import Tree, Label, Input, Button, Static, Log
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets.tree import TreeNode

from agentorg.utils.utils import postprocess_json
from agentorg.orchestrator.generator.prompts import *
from agentorg.utils.loader import Loader
import agentorg.agents
from agentorg.agents.agent import AGENT_REGISTRY


logger = logging.getLogger(__name__)

class InputModal(Screen):
    """A simple input modal for editing or adding tasks/steps."""
    
    def __init__(self, title: str, default: str = "", node=None, callback=None):
        super().__init__()
        self.title = title
        self.default = default
        self.result = default
        self.node = node
        self.callback = callback


    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.title, classes="title"),
            Input(value=self.default, id="input-field"),
            Horizontal(
                Button("Submit", id="submit"),
                Button("Cancel", id="cancel"),
                id="buttons"
            )
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.result = self.query_one("#input-field", Input).value
            # logger.debug(f"InputModal result: {self.result}")
        if self.callback:
            self.callback(self.result, self.node)
        logger.debug(f"InputModal result: {self.result}")
        self.app.pop_screen()  # Close modal

class TaskEditorApp(App):
    """A Textual app to edit tasks and steps in a hierarchical structure."""

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.task_tree: Tree[str] = None

    def compose(self) -> ComposeResult:
        self.task_tree = Tree("Tasks")
        self.task_tree.root.expand()

        # Populate the tree with tasks and steps
        for task in self.tasks:
            task_node = self.task_tree.root.add(task["task_name"], expand=True)
            for step in task["steps"]:
                task_node.add_leaf(step)

        yield self.task_tree
        yield Label("Click on a task or step to edit it. Press 'a' to add new item on the same level with the highlighted one, 'd' to delete the highlighted item, 'q' to exit.")

    def on_mount(self):
        self.task_tree.focus()

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        selected_node = event.node

        def handle_modal_result(result, node):
            if result is not None:  # Check if the user submitted a valid result
                node.set_label(result)  # Update the tree node's label
                self.call_later(self.update_tasks)  # Ensure task sync runs after UI update

        self.push_screen(
            InputModal(
                f"Edit '{selected_node.label}'", 
                default=str(selected_node.label), 
                node=selected_node,
                callback=handle_modal_result
            )
        )

    async def on_key(self, event):
        selected_node = self.task_tree.cursor_node
        if event.key == "a" and selected_node and selected_node.parent is not None:
            await self.action_add_node(selected_node)
        elif event.key == "d" and selected_node and selected_node.parent is not None:
            selected_node.remove()
            await self.update_tasks()
        elif event.key == "q":
            self.exit(self.tasks)  # Gracefully exit the app

    async def action_add_node(self, node: TreeNode):
        # if the node is a step node
        if node.parent.parent is not None:
            leaf = True
            node = node.parent
            title=f"Add new step under '{node.label.plain}'"
        else:  # if the node is a task node
            if node.is_expanded: # add step
                leaf = True
                node = node
                title=f"Enter new step under '{node.label.plain}'"
            else:
                leaf = False
                node = node.parent
                title=f"Add new task under '{node.label.plain}'"

        def handle_modal_result(result, node):
            if result is not None:  # Check if the user submitted a valid result
                if leaf:
                    node.add_leaf(result)
                else:
                    node.add(result, expand=True)
                self.call_later(self.update_tasks)  # Ensure task sync runs after UI update

        self.push_screen(
            InputModal(
                title, 
                default="",
                node=node,
                callback=handle_modal_result
            )
        )

    def show_input_modal(self, title: str, default: str = "") -> str:
        modal = InputModal(title, default)
        self.push_screen(modal)
        return modal.result

    async def update_tasks(self):
        self.tasks = []
        for task_node in self.task_tree.root.children:
            task_name = task_node.label.plain
            steps = [step.label.plain for step in task_node.children]
            self.tasks.append({"task_name": task_name, "steps": steps})

        log_message = f"Updated Tasks: {self.tasks}"
        logger.debug(log_message)




class Generator:
    def __init__(self, config, model):
        self.product_kwargs = json.load(open(config))
        self.role = self.product_kwargs.get("role")
        self.objective = self.product_kwargs.get("objective")
        self.intro = self.product_kwargs.get("intro")
        self.docs = self.product_kwargs.get("docs")
        self.tasks = self.product_kwargs.get("tasks")
        self.agents = self.product_kwargs.get("agents")
        self.model = model
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.orche_config_filepath = f"./agentorg/orchestrator/examples/{self.role}_taskgraph_{timestamp}.json"
        self.task_planning_filepath = f"./agentorg/orchestrator/examples/{self.role}_taskplanning_{timestamp}.json"
    

    def _generate_tasks(self):
        # based on the type and documents
        prompt = PromptTemplate.from_template(generate_tasks_sys_prompt)
        input_prompt = prompt.invoke({"role": self.role, "intro": self.intro, "docs": self.documents})
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
    
    def _format_task_graph(self, finetuned_best_practices):
        node_id = 1
        nodes = []
        edges = []
        task_ids = {}
        for best_practice, task in zip(finetuned_best_practices, self.tasks):
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
        return task_graph

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

        # Step 2: Generate the task planning
        best_practices = []
        for idx, task in progress_bar(enumerate(self.tasks), total=len(self.tasks)):
            logger.info(f"Generating best practice for task {idx}: {task}")
            best_practice = self._generate_best_practice(task)
            logger.info(f"Generated best practice for task {idx}: {best_practice}")
            best_practices.append(best_practice)

        # Step 3: iterate with user
        format_tasks = []
        for best_practice, task in zip(best_practices, self.tasks):
            task_name = task['task']
            steps = [bp["task"] for bp in best_practice]
            format_tasks.append({"task_name": task_name, "steps": steps})
        app = TaskEditorApp(format_tasks)
        hitl_result = app.run()
        json.dump(hitl_result, open(self.task_planning_filepath, "w"), indent=4)

        # Step 4: Pair task with agent
        finetuned_best_practices = []
        for idx_t, task in enumerate(hitl_result):
            steps = task["steps"]
            format_steps = []
            for idx_s, step in enumerate(steps):
                format_steps.append({
                    "step": idx_s + 1,
                    "task": step
                })
            finetuned_best_practice = self._finetune_best_practice(format_steps)
            logger.info(f"Finetuned best practice for task {idx_t}: {finetuned_best_practice}")
            finetuned_best_practices.append(finetuned_best_practice)

        # Step 5: Format the task graph
        task_graph = self._format_task_graph(finetuned_best_practices)

        with open(self.orche_config_filepath, "w") as f:
            json.dump(task_graph, f, indent=4)

        return self.orche_config_filepath