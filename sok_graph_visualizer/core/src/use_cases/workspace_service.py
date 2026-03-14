"""
WorkspaceService - provides workspace management functionality.

Manages workspaces in memory without database persistence.
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


class WorkspaceService:
    """
    Service for managing workspaces.
    
    Provides CRUD operations for workspaces without database persistence.
    All workspaces are stored in memory (no persistence between restarts).
    
    Attributes:
        workspaces (Dict[str, Workspace]): Dictionary mapping workspace IDs to Workspace objects
        active_workspace_id (Optional[str]): ID of the currently active workspace
    """
    
    def __init__(self):
        """Initialize the workspace service with empty storage."""
        self.workspaces: Dict[str, Workspace] = {}
        self.active_workspace_id: Optional[str] = None
    
    def create_workspace(
        self,
        name: str,
        base_graph=None,
        data_source_plugin: Optional[DataSourcePlugin] = None,
        visualizer_plugin: Optional[VisualizerPlugin] = None,
        metadata: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[str] = None,
        set_active: bool = True
    ) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            name: Name of the workspace
            base_graph: The initial graph (required)
            data_source_plugin: Active data source plugin
            visualizer_plugin: Active visualizer plugin
            metadata: Additional metadata
            workspace_id: Custom workspace ID (auto-generated if not provided)
            set_active: Whether to set this as the active workspace
            
        Returns:
            Created Workspace object
            
        Raises:
            ValueError: If workspace_id already exists or base_graph is missing
        """
        if base_graph is None:
            raise ValueError("base_graph is required to create a workspace")
        
        if workspace_id is None:
            workspace_id = str(uuid.uuid4())
        
        if workspace_id in self.workspaces:
            raise ValueError(f"Workspace with id '{workspace_id}' already exists")
        
        workspace = Workspace(
            workspace_id=workspace_id,
            base_graph=base_graph,
            name=name,
            data_source_plugin=data_source_plugin,
            visualizer_plugin=visualizer_plugin,
            metadata=metadata
        )
        
        self.workspaces[workspace_id] = workspace
        
        if set_active or self.active_workspace_id is None:
            self.active_workspace_id = workspace_id
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: ID of the workspace
            
        Returns:
            Workspace object or None if not found
        """
        return self.workspaces.get(workspace_id)
    
    def get_workspaces(self) -> List[Workspace]:
        """
        Get all workspaces.
        
        Returns:
            List of all Workspace objects
        """
        return list(self.workspaces.values())
    
    def remove_workspace(self, workspace_id: str) -> bool:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            
        Returns:
            True if successful, False if workspace not found
        """
        if workspace_id not in self.workspaces:
            return False
        
        del self.workspaces[workspace_id]
        
        # If we deleted the active workspace, clear active or set to another
        if self.active_workspace_id == workspace_id:
            if self.workspaces:
                self.active_workspace_id = next(iter(self.workspaces.keys()))
            else:
                self.active_workspace_id = None
        
        return True
    
    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Get the currently active workspace.
        
        Returns:
            Active Workspace object or None
        """
        if self.active_workspace_id:
            return self.workspaces.get(self.active_workspace_id)
        return None
    
    def set_active_workspace(self, workspace_id: str) -> bool:
        """
        Set the active workspace.
        
        Args:
            workspace_id: ID of the workspace to activate
            
        Returns:
            True if successful, False if workspace not found
        """
        if workspace_id not in self.workspaces:
            return False
        
        self.active_workspace_id = workspace_id
        return True
    
    def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        data_source_plugin: Optional[DataSourcePlugin] = None,
        visualizer_plugin: Optional[VisualizerPlugin] = None
    ) -> Optional[Workspace]:
        """
        Update workspace properties.
        
        Args:
            workspace_id: ID of the workspace to update
            name: New name (if provided)
            data_source_plugin: New data source plugin (if provided)
            visualizer_plugin: New visualizer plugin (if provided)
            
        Returns:
            Updated Workspace object or None if not found
        """
        workspace = self.get_workspace(workspace_id)
        if workspace is None:
            return None
        
        if name is not None:
            workspace.name = name
        if data_source_plugin is not None:
            workspace.data_source_plugin = data_source_plugin
        if visualizer_plugin is not None:
            workspace.visualizer_plugin = visualizer_plugin
        
        workspace.modified_at = datetime.now()
        return workspace
    
    def has_workspaces(self) -> bool:
        """
        Check if there are any workspaces.
        
        Returns:
            True if at least one workspace exists
        """
        return len(self.get_workspaces()) > 0
    
    def is_last_workspace(self, workspace_id: str) -> bool:
        """
        Check if this is the last remaining workspace.
        
        Args:
            workspace_id: ID of the workspace to check
            
        Returns:
            True if only one workspace exists
        """
        return len(self.get_workspaces()) <= 1
    
    def reset_workspace(self, workspace_id: Optional[str] = None) -> bool:
        """
        Reset a workspace to its base graph state.
        
        Args:
            workspace_id: ID of workspace to reset (uses active if not specified)
            
        Returns:
            bool: True if successful, False if workspace not found
        """
        if workspace_id is None:
            workspace_id = self.active_workspace_id
        
        if workspace_id is None or workspace_id not in self.workspaces:
            return False
        
        self.workspaces[workspace_id].reset()
        return True
    
    def undo(self, workspace_id: Optional[str] = None) -> bool:
        """
        Undo the last operation in a workspace.
        
        Args:
            workspace_id: ID of workspace (uses active if not specified)
            
        Returns:
            bool: True if successful, False otherwise
        """
        workspace = self._get_workspace_or_active(workspace_id)
        if workspace is None:
            return False
        
        return workspace.undo()
    
    def redo(self, workspace_id: Optional[str] = None) -> bool:
        """
        Redo the next operation in a workspace.
        
        Args:
            workspace_id: ID of workspace (uses active if not specified)
            
        Returns:
            bool: True if successful, False otherwise
        """
        workspace = self._get_workspace_or_active(workspace_id)
        if workspace is None:
            return False
        
        return workspace.redo()
    
    def _get_workspace_or_active(self, workspace_id: Optional[str] = None) -> Optional[Workspace]:
        """
        Get workspace by ID or return active workspace.
        
        Args:
            workspace_id: ID of workspace, or None for active
            
        Returns:
            Workspace object or None
        """
        if workspace_id is None:
            workspace_id = self.active_workspace_id
        
        if workspace_id is None:
            return None
        
        return self.workspaces.get(workspace_id)
    
    def clear_all(self) -> None:
        """Delete all workspaces."""
        self.workspaces.clear()
        self.active_workspace_id = None
    
    def __repr__(self) -> str:
        """Return string representation of the service."""
        return (
            f"WorkspaceService(workspaces={len(self.workspaces)}, "
            f"active={self.active_workspace_id})"
        )
