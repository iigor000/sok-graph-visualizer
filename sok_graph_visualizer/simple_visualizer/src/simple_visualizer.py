from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.api.model.Graph import Graph


# DTO objects for template

@dataclass
class NodeRef:
    """Simple reference to a node with just an id."""
    id: str


@dataclass
class VisualNode:
    node_id: str
    name: str
    attributes: Dict


@dataclass
class VisualEdge:
    edge_id: str
    node1: NodeRef  # source node reference
    node2: NodeRef  # target node reference
    attributes: Dict


# Simple Visualizer Plugin

class SimpleVisualizer(VisualizerPlugin):

    def __init__(self):
        templates_path = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(searchpath=templates_path),
            autoescape=select_autoescape()
        )

    def __str__(self):
        return "SimpleVisualizer"

    def get_name(self) -> str:
        return "Simple Visualizer"

    def get_description(self) -> str:
        return "Simple D3.js-based force-directed graph visualization"

    def render(self, graph: Graph) -> str:
        if graph is None:
            raise ValueError("Graph cannot be None")
        return self._visualize_graph(graph)
    

    def _visualize_graph(self, graph: Graph) -> str:
        template_file = (
            "simple_directed.jinja" if graph.directed else "simple.jinja"
        )
        template = self.env.get_template(template_file)

        prepared_nodes = self._prepare_nodes(graph)
        prepared_edges = self._prepare_edges(graph)

        return template.render(
            graph_nodes=prepared_nodes,
            graph_edges=prepared_edges,
        )


    # Helpers

    def _prepare_nodes(self, graph: Graph) -> Dict[str, VisualNode]:
        result: Dict[str, VisualNode] = {}

        for node_id, node in graph.nodes.items():
            result[node_id] = VisualNode(
                node_id=node.node_id,
                name=node.attributes.get("name", node_id),
                attributes=node.attributes,
            )

        return result

    def _prepare_edges(self, graph: Graph) -> Dict[str, VisualEdge]:
        result: Dict[str, VisualEdge] = {}

        for edge_id, edge in graph.edges.items():
            result[edge_id] = VisualEdge(
                edge_id=edge.edge_id,
                node1=NodeRef(id=edge.source),
                node2=NodeRef(id=edge.target),
                attributes=edge.attributes,
            )

        return result