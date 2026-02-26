from typing import Dict, Optional, Union
from datetime import date

AttributeValue = Union[int, str, float, date]

class Edge:
    """
    Represents an edge (connection) between two nodes in a graph.
    
    Supports both directed and undirected edges. An edge can have attributes
    to store additional information about the relationship.
    
    Attributes:
        edge_id (str): Unique identifier for the edge
        source (str): ID of the source node
        target (str): ID of the target node
        directed (bool): Whether the edge is directed
        attributes (Dict[str, AttributeValue]): Dictionary of edge attributes
    """
    
    def __init__(
        self,
        edge_id: str,
        source: str,
        target: str,
        attributes: Optional[Dict[str, AttributeValue]] = None
    ):
        """
        Initialize an Edge.
        
        Args:
            edge_id: Unique identifier for the edge
            source: ID of the source node
            target: ID of the target node
            directed: Whether the edge is directed (default: True)
            attributes: Optional dictionary of attributes
        """
        self.edge_id = edge_id
        self.source = source
        self.target = target
        self.attributes: Dict[str, AttributeValue] = attributes or {}
    
    def get_attribute(self, key: str) -> Optional[AttributeValue]:
        """Get the value of an attribute by key."""
        return self.attributes.get(key)
    
    def set_attribute(self, key: str, value: AttributeValue) -> None:
        """Set or update an attribute."""
        if not isinstance(value, (int, str, float, date)):
            raise TypeError(f"Attribute value must be int, str, float, or date. Got {type(value)}")
        self.attributes[key] = value
    
    def remove_attribute(self, key: str) -> None:
        """Remove an attribute by key."""
        if key in self.attributes:
            del self.attributes[key]
    
    def __repr__(self) -> str:
        return f"Edge(id={self.edge_id}, {self.source} -- {self.target}, attributes={self.attributes})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.edge_id == other.edge_id
    
    def __hash__(self) -> int:
        return hash(self.edge_id)
