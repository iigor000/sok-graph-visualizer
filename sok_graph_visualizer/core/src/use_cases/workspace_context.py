"""
WorkspaceContext - manages the active workspace and its operations.

Represents the current application context, tracking the active workspace
and providing operations on it.
"""

from typing import Optional, Dict, Any

from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.use_cases.workspace_service import WorkspaceService


class WorkspaceContext:
    """
    Context for the currently active workspace.
    
    Manages:
    - Which workspace is currently active
    - Graph context for the active workspace
    - Operations on the active workspace
    """
    
    def __init__(self, workspace_service: WorkspaceService):
        """
        Initialize the workspace context.
        
        Args:
            workspace_service: The workspace service to use
        """
        self.workspace_service = workspace_service
        self.current_workspace_id: Optional[str] = None
        
        # Initialize with first workspace if available
        workspaces = self.workspace_service.get_workspaces()
        if workspaces:
            self.current_workspace_id = workspaces[0].workspace_id
    
    def get_active_workspace(self) -> Optional[Workspace]:
        """
        Get the currently active workspace.
        
        Returns:
            Active Workspace object or None
        """
        if self.current_workspace_id is None:
            return None
        return self.workspace_service.get_workspace(self.current_workspace_id)
    
    def select_workspace(self, workspace_id: str) -> bool:
        """
        Switch to a different workspace.
        
        Args:
            workspace_id: ID of the workspace to switch to
            
        Returns:
            True if successful, False if workspace not found
        """
        workspace = self.workspace_service.get_workspace(workspace_id)
        if workspace is None:
            return False
        
        self.current_workspace_id = workspace_id
        return True
    
    def select_first_workspace(self) -> bool:
        """
        Switch to the first available workspace.
        
        Returns:
            True if successful, False if no workspaces exist
        """
        workspaces = self.workspace_service.get_workspaces()
        if not workspaces:
            self.current_workspace_id = None
            return False
        
        self.current_workspace_id = workspaces[0].workspace_id
        return True
    
    def is_last_workspace(self) -> bool:
        """
        Check if the current workspace is the last one.
        
        Returns:
            True if only one workspace exists
        """
        return len(self.workspace_service.get_workspaces()) <= 1
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get context information about the active workspace.
        
        Returns:
            Dictionary with current workspace context
        """
        workspace = self.get_active_workspace()
        if workspace is None:
            return {
                "current_workspace_id": None,
                "current_workspace": None,
                "active": False
            }
        
        return {
            "current_workspace_id": workspace.workspace_id,
            "current_workspace": {
                "id": workspace.workspace_id,
                "name": workspace.name,
                "nodes_count": len(workspace.current_graph.nodes) if workspace.current_graph else 0,
                "edges_count": len(workspace.current_graph.edges) if workspace.current_graph else 0,
            },
            "active": True
        }
    
    def has_active_workspace(self) -> bool:
        """
        Check if an active workspace is set.
        
        Returns:
            True if an active workspace exists
        """
        return self.get_active_workspace() is not None
