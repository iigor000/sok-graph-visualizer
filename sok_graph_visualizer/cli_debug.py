from sok_graph_visualizer.core.src.app import App

from sok_graph_visualizer.platform.cli.cli_terminal import CLITerminal
from sok_graph_visualizer.platform.cli.cli_parser import CLIParser
from sok_graph_visualizer.platform.cli.cli_executor import CLIExecutor

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge

def main():

    app = App()

    graph = Graph(graph_id="test_graph")

    n1 = Node(node_id="1", attributes={"Name": "Alice"})
    n2 = Node(node_id="2", attributes={"Name": "Tom"})

    graph.add_node(n1)
    graph.add_node(n2)

    graph.add_edge(
        Edge(
            edge_id="1",
            source="1",
            target="2",
            attributes={"Name": "Friends"}
        )
    )

    app.workspace_manager.create_workspace(
        base_graph=graph,
        name="test"
    )

    parser = CLIParser()
    executor = CLIExecutor(app)

    terminal = CLITerminal(app, parser, executor)

    terminal.run()

if __name__ == "__main__":
    main()