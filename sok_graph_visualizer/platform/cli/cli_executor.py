from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge


class CLIExecutor:
    """
    CLI Executor koji koristi registry komandi.
    """

    def __init__(self, app):
        self.app = app
        self.commands = {
            "create_node": self._create_node,
            "edit_node": self._edit_node,
            "delete_node": self._delete_node,
            "create_edge": self._create_edge,
            "edit_edge": self._edit_edge,
            "delete_edge": self._delete_edge,
            "clear": self._clear_graph,
            "filter": self._filter_graph,
            "search": self._search_graph,
        }

    def execute(self, command):
        handler = self.commands.get(command.name)
        if not handler:
            print(f"Unknown command: {command.name}")
            return
        try:
            handler(command.params)
        except Exception as e:
            print(f"Error: {e}")

    def _get_active_graph(self):
        workspace = self.app.workspace_manager.get_active_workspace()
        if workspace is None:
            raise ValueError("No active workspace")
        return workspace, workspace.current_graph

    def _create_node(self, params):
        workspace, graph = self._get_active_graph()
        node = Node(node_id=params["id"], attributes=params.get("properties", {}))
        graph.add_node(node)
        print(f"Node {params['id']} created")

    def _edit_node(self, params):
        workspace, graph = self._get_active_graph()
        node = graph.get_node(params["id"])
        if not node:
            print("Node not found")
            return
        node.attributes.update(params.get("properties", {}))
        print(f"Node {params['id']} updated")

    def _delete_node(self, params):
        workspace, graph = self._get_active_graph()
        graph.remove_node(params["id"])
        print(f"Node {params['id']} deleted")

    def _create_edge(self, params):
        workspace, graph = self._get_active_graph()
        edge = Edge(
            edge_id=params["id"],
            source=params["source"],
            target=params["target"],
            attributes=params.get("properties", {})
        )
        graph.add_edge(edge)
        print(f"Edge {params['id']} created")

    def _edit_edge(self, params):
        workspace, graph = self._get_active_graph()
        edge = graph.get_edge(params["id"])
        if not edge:
            print("Edge not found")
            return
        edge.attributes.update(params.get("properties", {}))
        print(f"Edge {params['id']} updated")

    def _delete_edge(self, params):
        workspace, graph = self._get_active_graph()
        graph.remove_edge(params["id"])
        print(f"Edge {params['id']} deleted")

    def _clear_graph(self, params):
        workspace, graph = self._get_active_graph()
        graph.nodes.clear()
        graph.edges.clear()
        graph._adjacency_list.clear()
        print("Graph cleared")

    def _filter_graph(self, params):
        print(f"Filter expression: {params['expression']}")

    def _search_graph(self, params):
        print(f"Search expression: {params['expression']}")