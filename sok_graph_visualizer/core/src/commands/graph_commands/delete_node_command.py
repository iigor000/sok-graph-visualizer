from typing import Any, Dict, Tuple
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager
from sok_graph_visualizer.api.model.Node import Node

class DeleteNodeCommand(Command):
    """
    Command to delete an existing node from the current graph in the active workspace.

    This command retrieves the active workspace, looks up the node by ID,
    and removes it from the graph if it exists. 

    Attributes:
        workspace_manager (WorkspaceManager): Manager to access the active workspace.
        args (Dict[str, Any]): Dictionary containing command parameters:
            - id (str): Identifier of the node to be deleted.
    """
    def __init__(self, workspace_manager: WorkspaceManager, args: Dict[str, Any]):
        """
        Initialize the DeleteNodeCommand.

        Args:
            workspace_manager (WorkspaceManager): Manager used to retrieve the active workspace.
            args (Dict[str, Any]): Dictionary containing the node ID to delete.
        """
        self.workspace_manager = workspace_manager
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the node deletion operation.

        Steps:
            1. Retrieve the active workspace.
            2. If no workspace is active, return failure.
            3. Access the current graph from the workspace.
            4. Retrieve the node ID from the command arguments.
            5. Look up the node in the graph:
                - If the node does not exist, return failure.
            6. Remove the node from the graph.
            7. Return success flag and a descriptive message.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the node was deleted successfully, False otherwise.
                - message (str): Human-readable description of the result.
        """

        workspace = self.workspace_manager.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        node_id = self.args.get("id")
        node = graph.get_node(node_id)

        if not node:
            return False, f"Node {node_id} not found"
        
        graph.remove_node(node_id)

        return True, f"Node {node_id} deleted."