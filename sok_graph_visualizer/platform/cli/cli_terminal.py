from sok_graph_visualizer.core.src.app import App

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge

class CLITerminal:
    def __init__(self, app, parser, executor):
        self.app = app
        self.parser = parser
        self.executor = executor

    def print_graph(self):

        workspace = self.app.workspace_manager.get_active_workspace()

        if workspace is None:
            print("No active workspace")
            return

        graph = workspace.current_graph

        print("\n--- GRAPH ---")

        print("Nodes:")
        for node in graph.nodes.values():
            print(f"{node.node_id} -> {node.attributes}")

        print("\nEdges:")
        for edge in graph.edges.values():
            print(f"{edge.edge_id}: {edge.source} -> {edge.target} {edge.attributes}")

        print("-------------\n")


    def run(self):
        while True:
            command = input("> ")

            if command == "exit":
                break

            parsed = self.parser.parse(command)

            self.executor.execute(parsed)

            self.print_graph()