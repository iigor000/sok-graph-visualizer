from datetime import date
from typing import Dict, Set, Tuple
from sok_graph_visualizer.api.model import Node
from sok_graph_visualizer.api.model.Graph import Graph


class GraphQueryService:
    """
    Service responsible for search and filter operations over a graph.

    Both operations return a subgraph of the input graph.
    """

    _SUPPORTED_OPERATORS = ["==", "!=", ">=", "<=", ">", "<"]

    def filter(self, current_graph : Graph, query : str) -> Graph:
        """
        Filter nodes using an expression of the form:
            <attribute_name> <operator> <value>

        Supported operators:
            ==, !=, >, >=, <, <=

        Args:
            graph: Input graph.
            expression: Filter expression.

        Returns:
            Graph: Subgraph containing matching nodes.
        """
        if not query or not(isinstance(query, str)):
            raise ValueError("Filter query must be a non-empty string.")
        
        attribute_name, operator, value = self._parse_filter_expression(query)
        matching_node_ids : Set[str] = set()

        for node in current_graph.nodes.values():
            if self._node_matches_filter(node, attribute_name, operator, value):
                matching_node_ids.add(node)

            return current_graph.get_subgraph(matching_node_ids)


    def search(self, current_graph : Graph, query : str) -> Graph:
        """
        Search nodes by arbitrary text.

        A node matches if the query is contained in:
        - an attribute name
        - or an attribute value (converted to string)

        Args:
            graph: Input graph.
            query: Arbitrary search text.

        Returns:
            Graph: Subgraph containing matching nodes.
        """
        if not query or not(isinstance(query, str)):
            raise ValueError("Search query must be a non-empty string.")
        
        normalized_query = query.strip().lower()
        matching_node_ids : Set[str] = set()

        for node in current_graph.nodes.values():
            if self._node_matches_search(node, normalized_query):
                matching_node_ids.add(node.node_id)

        return current_graph.get_subgraph(matching_node_ids)
    
    def _node_matches_search(node : Node, query : str) -> bool:
        """
        Check if a node matches the search query.
        """
        for attr_name, attr_value in node.attributes.items():
            if query in attr_name.lower():
                return True
            if query in str(attr_value).lower():
                return True
        return False
    
    def _parse_filter_expression(self, expression: str) -> Tuple[str, str, str]:
        """
        Parse filter expression into:
            (attribute_name, operator, raw_value)

        Example:
            'age >= 25' -> ('age', '>=', '25')
        """
        expression = expression.strip()

        for operator in self._SUPPORTED_OPERATORS:
            if operator in expression:
                left, right = expression.split(operator, 1)
                attribute_name = left.strip()
                raw_value = right.strip()

                if not attribute_name or not raw_value:
                    raise ValueError(
                        "Invalid filter expression. Expected format: "
                        "<attribute_name> <operator> <value>"
                    )

                return attribute_name, operator, raw_value

        raise ValueError(
            "Invalid filter expression. Supported operators are: ==, !=, >, >=, <, <="
        )

    def _node_matches_filter(
        self,
        node: Node,
        attribute_name: str,
        operator: str,
        raw_value: str
    ) -> bool:
        """
        Check if a node matches the filter expression.
        """
        if attribute_name not in node.attributes:
            return False

        actual_value = node.attributes[attribute_name]
        typed_value = self._convert_to_attribute_type(raw_value, actual_value)

        return self._evaluate(operator, actual_value, typed_value)

    def _convert_to_attribute_type(self, raw_value: str, actual_value):
        """
        Convert raw string value to the type of the node attribute.

        Supported attribute types:
            int, float, str, date
        """
        try:
            if isinstance(actual_value, bool):
                raise ValueError("Boolean attributes are not supported.")

            if isinstance(actual_value, int):
                return int(raw_value)

            if isinstance(actual_value, float):
                return float(raw_value)

            if isinstance(actual_value, date):
                return date.fromisoformat(raw_value)

            if isinstance(actual_value, str):
                return raw_value

        except Exception:
            raise ValueError(
                f"Invalid value type for attribute. Expected value compatible with "
                f"{type(actual_value).__name__}."
            )

        raise ValueError(
            f"Unsupported attribute type: {type(actual_value).__name__}"
        )

    def _evaluate(self, operator: str, left, right) -> bool:
        """
        Evaluate comparison between two typed values.
        """
        if operator == "==":
            return left == right
        if operator == "!=":
            return left != right
        if operator == ">":
            return left > right
        if operator == ">=":
            return left >= right
        if operator == "<":
            return left < right
        if operator == "<=":
            return left <= right

        raise ValueError(f"Unsupported operator: {operator}")