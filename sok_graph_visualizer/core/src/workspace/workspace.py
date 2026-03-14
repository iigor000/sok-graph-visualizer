"""
Workspace class for managing graph state, plugins, and operations.
"""

from typing import Dict, Optional, Any, List
from copy import deepcopy
from datetime import datetime

from .operation import Operation

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


class Workspace:
    """
    Represents a workspace for graph manipulation.
    
    A workspace encapsulates:
    - Base graph (the original, unmodified graph)
    - Current graph (the working graph with transformations applied)
    - Active data source plugin
    - Active visualizer plugin
    - Operation history (stack of operations for undo functionality)
    - Selected node information
    - Metadata (parameters and other workspace state)
    
    Attributes:
        workspace_id (str): Unique identifier for the workspace
        name (str): Human-readable name for the workspace
        base_graph: The original graph
        current_graph: The current state of the graph
        data_source_plugin (Optional[DataSourcePlugin]): Active data source plugin for the workspace
        visualizer_plugin (Optional[VisualizerPlugin]): Active visualizer plugin for the workspace
        operation_history (List[Operation]): History of operations performed
        current_operation_index (int): Current position in operation history (for undo/redo)
        selected_node_id (Optional[str]): ID of currently selected node
        metadata (Dict[str, Any]): Additional metadata
    """
    
    def __init__(
        self,
        workspace_id: str,
        base_graph : Graph,
        name: str = "",
        data_source_plugin: Optional[DataSourcePlugin] = None,
        visualizer_plugin: Optional[VisualizerPlugin] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Workspace.
        
        Args:
            workspace_id: Unique identifier for the workspace
            base_graph: The initial graph to work with
            name: Human-readable name (defaults to workspace_id)
            data_source_plugin: Active data source plugin for this workspace
            visualizer_plugin: Active visualizer plugin for this workspace
            metadata: Additional metadata dictionary
        """
        self.workspace_id = workspace_id
        self.name = name or workspace_id
        self.base_graph = deepcopy(base_graph)
        self.current_graph = deepcopy(base_graph)
        self.data_source_plugin = data_source_plugin
        self.visualizer_plugin = visualizer_plugin
        self.operation_history: List[Operation] = []
        self.current_operation_index = -1  # -1 means at base state
        self.selected_node_id: Optional[str] = None
        self.metadata: Dict[str, Any] = metadata or {}
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
    
    def apply_operation(
        self,
        new_graph,
        operation_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = ""
    ) -> None:
        """
        Apply a new operation to the workspace.
        
        This method:
        1. Truncates any operations after the current position (for redo)
        2. Adds the new operation to history
        3. Updates the current graph
        
        Args:
            new_graph: The resulting graph after the operation
            operation_type: Type of operation performed
            parameters: Parameters used in the operation
            description: Human-readable description
        """
        # If we're not at the end of history, truncate everything after current position
        if self.current_operation_index < len(self.operation_history) - 1:
            self.operation_history = self.operation_history[:self.current_operation_index + 1]
        
        # Create and add new operation
        operation = Operation(
            operation_type=operation_type,
            parameters=parameters,
            description=description
        )
        self.operation_history.append(operation)
        self.current_operation_index += 1
        
        # Update current graph
        self.current_graph = deepcopy(new_graph)
        self.modified_at = datetime.now()
    
    def undo(self) -> bool:
        """
        Undo the last operation.
        
        Returns:
            bool: True if undo was successful, False if at base state
        """
        if self.current_operation_index < 0:
            return False  # Already at base state
        
        self.current_operation_index -= 1
        self._rebuild_current_graph()
        self.modified_at = datetime.now()
        return True
    
    def redo(self) -> bool:
        """
        Redo the next operation.
        
        Returns:
            bool: True if redo was successful, False if at end of history
        """
        if self.current_operation_index >= len(self.operation_history) - 1:
            return False  # Already at end of history
        
        self.current_operation_index += 1
        self._rebuild_current_graph()
        self.modified_at = datetime.now()
        return True
    
    def reset(self) -> None:
        """
        Reset the workspace to the base graph state.
        
        This clears all operations and resets the current graph to the base graph.
        """
        self.current_graph = deepcopy(self.base_graph)
        self.operation_history.clear()
        self.current_operation_index = -1
        self.selected_node_id = None
        self.modified_at = datetime.now()
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.current_operation_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.current_operation_index < len(self.operation_history) - 1
    
    def get_current_operation(self) -> Optional[Operation]:
        """Get the current operation in history."""
        if self.current_operation_index >= 0 and self.current_operation_index < len(self.operation_history):
            return self.operation_history[self.current_operation_index]
        return None
    
    def set_selected_node(self, node_id: Optional[str]) -> None:
        """
        Set the currently selected node.
        
        Args:
            node_id: ID of the node to select, or None to deselect
        """
        if node_id is not None and node_id not in self.current_graph.nodes:
            raise ValueError(f"Node '{node_id}' does not exist in current graph")
        self.selected_node_id = node_id
        self.modified_at = datetime.now()

    def set_data_source_plugin(self, plugin: Optional[DataSourcePlugin]) -> None:
        """Set the active data source plugin for this workspace."""
        self.data_source_plugin = plugin
        self.modified_at = datetime.now()

    def set_visualizer_plugin(self, plugin: Optional[VisualizerPlugin]) -> None:
        """Set the active visualizer plugin for this workspace."""
        self.visualizer_plugin = plugin
        self.modified_at = datetime.now()
    
    def get_selected_node(self):
        """Get the currently selected node object."""
        if self.selected_node_id:
            return self.current_graph.get_node(self.selected_node_id)
        return None
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update workspace metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.modified_at = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get workspace metadata.
        
        Args:
            key: Metadata key
            default: Default value if key doesn't exist
            
        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)
    
    def __repr__(self) -> str:
        return (
            f"Workspace(id={self.workspace_id}, name={self.name}, "
            f"operations={len(self.operation_history)}, "
            f"position={self.current_operation_index + 1})"
        )
