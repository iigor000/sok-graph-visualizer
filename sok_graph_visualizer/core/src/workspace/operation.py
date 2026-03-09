"""
Operation class for tracking graph transformations.
"""

from typing import Dict, Optional, Any
from datetime import datetime
import uuid


class Operation:
    """
    Represents a single operation performed on a graph.
    
    Attributes:
        operation_id (str): Unique identifier for the operation
        operation_type (str): Type of operation (e.g., 'add_node', 'remove_edge', 'plugin_transform')
        timestamp (datetime): When the operation was performed
        plugin_name (Optional[str]): Name of the plugin that performed the operation
        parameters (Dict[str, Any]): Parameters used in the operation
        description (str): Human-readable description of the operation
    """
    
    def __init__(
        self,
        operation_type: str,
        plugin_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = ""
    ):
        """
        Initialize an Operation.
        
        Args:
            operation_type: Type of operation
            plugin_name: Name of the plugin (if applicable)
            parameters: Operation parameters
            description: Human-readable description
        """
        self.operation_id = str(uuid.uuid4())
        self.operation_type = operation_type
        self.timestamp = datetime.now()
        self.plugin_name = plugin_name
        self.parameters = parameters or {}
        self.description = description or operation_type
    
    def __repr__(self) -> str:
        plugin_info = f", plugin={self.plugin_name}" if self.plugin_name else ""
        return f"Operation(type={self.operation_type}{plugin_info}, time={self.timestamp})"
