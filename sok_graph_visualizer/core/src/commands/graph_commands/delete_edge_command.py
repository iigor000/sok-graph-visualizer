from typing import Any, Dict, Tuple
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager

class DeleteEdgeCommand(Command):
    """
    Command to delete an existing edge from the current graph in the active workspace.

    This command retrieves the active workspace, looks up the edge by ID,
    and removes it from the current graph if it exists.

    Attributes:
        workspace_manager (WorkspaceManager): Manager to access the active workspace.
        args (Dict[str, Any]): Dictionary containing command parameters:
            - id (str): Identifier of the edge to be deleted.
    """

    def __init__(self, workspace_manager: WorkspaceManager, args: Dict[str, Any]):
        """
        Initialize the DeleteEdgeCommand.

        Args:
            workspace_manager (WorkspaceManager): Manager to retrieve the active workspace.
            args (Dict[str, Any]): Dictionary containing the edge ID to delete.
        """
        self.workspace_manager = workspace_manager
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the edge deletion operation.

        Steps:
            1. Retrieve the active workspace.
            2. If no workspace is active, return failure.
            3. Access the current graph.
            4. Retrieve the edge ID from args.
            5. Look up the edge in the graph:
                - If the edge does not exist, return failure.
            6. Remove the edge from the graph.
            7. Return success flag and a confirmation message.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the edge was deleted successfully, False otherwise.
                - message (str): Human-readable description of the result.
        """
        workspace = self.workspace_manager.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        edge_id = self.args.get("id")
        edge = graph.get_edge(edge_id)
        if not edge:
            return False, f"Edge {edge_id} not found"

        graph.remove_edge(edge_id)

        return True, f"Edge {edge_id} deleted"
    