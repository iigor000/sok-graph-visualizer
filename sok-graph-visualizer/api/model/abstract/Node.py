from typing import Dict, Optional, Union
from datetime import date

AttributeValue = Union[int, str, float, date]

class Node:
    """
    Represents a node (vertex) in a graph.
    
    Each node has a unique identifier and a dictionary of attributes.
    Attributes can be of type int, str, float, or date.
    
    Attributes:
        node_id (str): Unique identifier for the node
        attributes (Dict[str, AttributeValue]): Dictionary of node attributes
    """
    
    def __init__(self, node_id: str, attributes: Optional[Dict[str, AttributeValue]] = None):
        """
        Initialize a Node.
        
        Args:
            node_id: Unique identifier for the node
            attributes: Optional dictionary of attributes
        """
        self.node_id = node_id
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
        return f"Node(id={self.node_id}, attributes={self.attributes})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id
    
    def __hash__(self) -> int:
        return hash(self.node_id)
