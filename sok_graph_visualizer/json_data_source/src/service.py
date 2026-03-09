from datetime import datetime, date
import itertools
from typing import Any, Dict, Set

from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.api.model.Graph import Graph


class JsonGraphParserService:
    """
    Service that parses JSON data and converts it into the platform's Graph model.

    Responsibilities:
    - Collects all IDs ("@id") in the JSON to manage references between nodes.
    - Creates nodes (Node) for objects and their attributes.
    - Creates edges (Edge) for references to other objects.
    - Handles lists, nested dictionaries, and literal values.
    - Automatically generates IDs for nodes that do not have "@id".

    Main method:
    - parse(data: Dict, graph: Graph) -> Graph:
        Parses the JSON data into a Graph object.
    """

    def __init__(self):
        self.id_node_map: Dict[str, Node] = {}
        self.known_ids: Set[str] = set()
        self.pending_edges = []

        self.edge_counter = itertools.count()
        self.node_counter = itertools.count()

        self.graph: Graph | None = None

    def _collect_ids(self, obj):
        """
        Recursively traverses the JSON object and collects all "@id" values
        into the known_ids set, which is used to create edges between nodes.
        """

        if isinstance(obj, dict):

            if "@id" in obj:
                self.known_ids.add(str(obj["@id"]))

            for v in obj.values():
                self._collect_ids(v)

        elif isinstance(obj, list):
            for item in obj:
                self._collect_ids(item)

    def _generate_edge_id(self):
        """Generates a unique ID for a node that does not have an "@id"."""

        return f"e_{next(self.edge_counter)}"

    def _generate_node_id(self):
        """Generates a unique ID for each edge (Edge) in the graph."""

        return f"auto_{next(self.node_counter)}"

    def _normalize_value(self, value):
        """
        Converts string values in ISO date format to datetime objects.
        Leaves integers, floats, and date/datetime objects unchanged.
        Converts other complex types to string.
        """

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return value

        if isinstance(value, (int, float, date, datetime)):
            return value

        return str(value)

    def _build(self, obj, parent_id=None, relation=None):
        """
        Recursively builds nodes and edges from a JSON object.
        - Nested dictionaries or lists are processed recursively.
        - References to "@id" create edges.
        - Literal values become node attributes.
        """

        if not isinstance(obj, dict):
            return

        node_id = obj.get("@id")

        if node_id is None:
            node_id = "root" if parent_id is None else self._generate_node_id()

        node_id = str(node_id)

        if parent_id is not None and relation is not None:
            # for same id on diference places
            if str(parent_id) != node_id:
                hierarchy_edge = Edge(
                    edge_id=self._generate_edge_id(),
                    source=str(parent_id),
                    target=node_id,
                    attributes={"relation": relation}
                )
                self.pending_edges.append(hierarchy_edge)

        attributes = {}
        children = []

        for key, value in obj.items():

            if key == "@id":
                continue

            if isinstance(value, dict):
                children.append((value, key))

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        children.append((item, key))
                    elif isinstance(item, str) and item in self.known_ids:
                        if item != node_id:
                            list_edge = Edge(
                                edge_id=self._generate_edge_id(),
                                source=node_id,
                                target=item,
                                attributes={"relation": key}
                            )
                            self.pending_edges.append(list_edge)
                    else:
                        normalized = self._normalize_value(item)
                        if key not in attributes:
                            attributes[key] = []
                        
                        if isinstance(attributes[key], list):
                            attributes[key].append(normalized)

            elif isinstance(value, str) and value in self.known_ids:
                if value != node_id:
                    edge = Edge(
                        edge_id=self._generate_edge_id(),
                        source=node_id,
                        target=value,
                        attributes={"relation": key}
                    )

                    self.pending_edges.append(edge)

            else:
                attributes[key] = self._normalize_value(value)

        # node creation
        if node_id not in self.id_node_map:

            node = Node(
                node_id=node_id,
                attributes=attributes
            )

            self.graph.add_node(node)
            self.id_node_map[node_id] = node
        else:
            existing_node = self.id_node_map[node_id]
            for key, value in attributes.items():
                existing_node.attributes[key] = value

        # traversal
        for child_obj, rel in children:
            self._build(child_obj, node_id, rel)


    def parse(self, data: Dict, graph: Graph):
        self.graph = graph
        self._collect_ids(data)
        root_obj = data.get("root", data)
        self._build(root_obj)

        for edge in self.pending_edges:
            self.graph.add_edge(edge)

        return graph