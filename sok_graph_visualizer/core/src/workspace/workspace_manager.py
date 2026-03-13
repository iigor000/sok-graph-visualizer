"""
WorkspaceManager class for managing multiple workspaces.
"""

from typing import Dict, Optional, Any, List
import uuid

from .workspace import Workspace
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


class WorkspaceManager:
    """
    Manages multiple workspaces.
    
    The WorkspaceManager is responsible for:
    - Creating and deleting workspaces
    - Switching between workspaces
    - Managing workspace lifecycle
    
    Attributes:
        workspaces (Dict[str, Workspace]): Dictionary mapping workspace IDs to Workspace objects
        active_workspace_id (Optional[str]): ID of the currently active workspace
    """
    
    def __init__(self):
        """Initialize a WorkspaceManager."""
        self.workspaces: Dict[str, Workspace] = {}
        self.active_workspace_id: Optional[str] = None
    
    def create_workspace(
        self,
        base_graph,
        workspace_id: Optional[str] = None,
        name: str = "",
        data_source_plugin: Optional[DataSourcePlugin] = None,
        visualizer_plugin: Optional[VisualizerPlugin] = None,
        metadata: Optional[Dict[str, Any]] = None,
        set_active: bool = True
    ) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            base_graph: The initial graph for the workspace
            workspace_id: Unique identifier (auto-generated if not provided)
            name: Human-readable name
            data_source_plugin: Active data source plugin for the workspace
            visualizer_plugin: Active visualizer plugin for the workspace
            metadata: Additional metadata
            set_active: Whether to set this as the active workspace
            
        Returns:
            The created Workspace object
            
        Raises:
            ValueError: If workspace_id already exists
        """
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
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            
        Returns:
            bool: True if workspace was deleted, False if not found
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
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: ID of the workspace
            
        Returns:
            Workspace object or None if not found
        """
        return self.workspaces.get(workspace_id)
    
    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Get the currently active workspace.
        
        Returns:
            Active Workspace object or None if no active workspace
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
            bool: True if successful, False if workspace not found
        """
        if workspace_id not in self.workspaces:
            return False
        
        self.active_workspace_id = workspace_id
        return True
    
    def list_workspaces(self) -> List[Workspace]:
        """
        Get a list of all workspaces.
        
        Returns:
            List of Workspace objects
        """
        return list(self.workspaces.values())
    
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
        return (
            f"WorkspaceManager(workspaces={len(self.workspaces)}, "
            f"active={self.active_workspace_id})"
        )
