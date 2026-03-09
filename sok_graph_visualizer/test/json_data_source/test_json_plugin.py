import os
import pytest

from sok_graph_visualizer.json_data_source.src.implementation import JsonDataSourcePlugin


def test_json_plugin_parse():
    """
    Simple test that:
    - Loads a JSON file with test data.
    - Parses it through JsonDataSourcePlugin.
    - Checks that the resulting graph has nodes and edges.
    - Prints the graph structure for visual inspection.
    """
    file_path = "sok_graph_visualizer/test/data/test_graph.json"

    plugin = JsonDataSourcePlugin({
        "file_path": file_path
    })

    graph = plugin.parse()

    # Basic assertions
    assert graph is not None
    assert len(graph.nodes) > 0

    print("\n===== GRAPH STRUCTURE =====")
    print(f"Nodes count: {len(graph.nodes)}")
    print(f"Edges count: {len(graph.edges)}")

    print("\nNodes:")
    for node_id, node in graph.nodes.items():
        print(f"{node_id} -> {node.attributes}")

    print("\nEdges:")
    for edge_id, edge in graph.edges.items():
        print(
            f"{edge_id}: {edge.source} -> {edge.target} | attrs={edge.attributes}"
        )