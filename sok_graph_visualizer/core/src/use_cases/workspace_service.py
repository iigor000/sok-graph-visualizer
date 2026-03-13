"""
WorkspaceService - provides workspace management functionality.

Wraps WorkspaceManager to provide a clean service layer.
Since there's no database, everything is stored in memory (dictionary).
"""

from typing import List, Optional, Dict, Any

from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


class WorkspaceService:
    """
    Service for managing workspaces.
    
    Provides CRUD operations for workspaces without database persistence.
    All workspaces are stored in memory (no persistence between restarts).
    """
    
    def __init__(self):
        """Initialize the workspace service with an empty manager."""
        self.workspace_manager = WorkspaceManager()
    
    def create_workspace(
        self,
        name: str,
        base_graph=None,
        data_source_plugin: Optional[DataSourcePlugin] = None,
        visualizer_plugin: Optional[VisualizerPlugin] = None,
        metadata: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[str] = None
    ) -> Workspace:
        """
        Create a new workspace.
        
        Args:
            name: Name of the workspace
            base_graph: The initial graph (required unless already has one)
            data_source_plugin: Active data source plugin
            visualizer_plugin: Active visualizer plugin
            metadata: Additional metadata
            workspace_id: Custom workspace ID (auto-generated if not provided)
            
        Returns:
            Created Workspace object
        """
        if base_graph is None:
            raise ValueError("base_graph is required to create a workspace")
        
        return self.workspace_manager.create_workspace(
            base_graph=base_graph,
            workspace_id=workspace_id,
            name=name,
            data_source_plugin=data_source_plugin,
            visualizer_plugin=visualizer_plugin,
            metadata=metadata
        )
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: ID of the workspace
            
        Returns:
            Workspace object or None if not found
        """
        return self.workspace_manager.get_workspace(workspace_id)
    
    def get_workspaces(self) -> List[Workspace]:
        """
        Get all workspaces.
        
        Returns:
            List of all Workspace objects
        """
        return self.workspace_manager.list_workspaces()
    
    def remove_workspace(self, workspace_id: str) -> bool:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            
        Returns:
            True if successful, False if workspace not found
        """
        return self.workspace_manager.delete_workspace(workspace_id)
    
    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Get the currently active workspace.
        
        Returns:
            Active Workspace object or None
        """
        return self.workspace_manager.get_active_workspace()
    
    def set_active_workspace(self, workspace_id: str) -> bool:
        """
        Set the active workspace.
        
        Args:
            workspace_id: ID of the workspace to activate
            
        Returns:
            True if successful, False if workspace not found
        """
        return self.workspace_manager.set_active_workspace(workspace_id)
    
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
        
        workspace.modified_at = __import__('datetime').datetime.now()
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
