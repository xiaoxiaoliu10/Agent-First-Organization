from typing import List, Tuple
from arklex.utils.graph_state import NodeInfo, Params, PathNode, StatusEnum


NESTED_GRAPH_ID = "nested_graph"

class NestedGraph:
    def __init__(self, node_info: NodeInfo):
        self.node_info = node_info

    def get_nested_graph_start_node_id(self):
        return str(self.node_info.attributes["value"])
    
    @staticmethod
    def get_nested_graph_component_node(params: Params, is_leaf_func) -> Tuple[PathNode | None, Params]:
        def _get_nested_graph_component_node(node_i, params: Params) -> Tuple[int, Params]:
            """
            if node in nested graph, return nested graph node, params and update path
            if node in main graph, return Nonde, params
            """
            path: List[PathNode] = params.taskgraph.path
            cur_node_i = node_i
            prev_node_id = None
            while cur_node_i >= 0:
                if path[cur_node_i].nested_graph_leaf_jump is not None:
                    cur_node_i = path[cur_node_i].nested_graph_leaf_jump

                cur_node: PathNode = path[cur_node_i]
                cur_node_id = cur_node.node_id
                to_node_id = cur_node.nested_graph_node_value
                if to_node_id is not None and to_node_id == prev_node_id:
                    params.taskgraph.node_status[cur_node_id] = StatusEnum.COMPLETE
                    params.taskgraph.path[node_i].nested_graph_leaf_jump = cur_node_i
                    return cur_node_i, params
                prev_node_id = cur_node_id
                cur_node_i -= 1

            return -1, params
        
        path = params.taskgraph.path
        cur_node_i = len(path) - 1
        while cur_node_i >= 0:
            nested_graph_next_node_path_i, params = _get_nested_graph_component_node(cur_node_i, params)
            if nested_graph_next_node_path_i == -1:
                path_node: PathNode = path[cur_node_i]
                return path_node, params
            path_node: PathNode = path[nested_graph_next_node_path_i]
            node_id = path_node.node_id
            if not is_leaf_func(node_id):
                return path_node, params
            cur_node_i = nested_graph_next_node_path_i
       
        return None, params