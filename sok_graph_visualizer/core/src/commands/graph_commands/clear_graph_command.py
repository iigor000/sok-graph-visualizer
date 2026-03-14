from typing import Any, Dict, Tuple
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.use_cases.workspace_context import WorkspaceContext

class ClearGraphCommand(Command):
    """
    Command to clear all nodes and edges from the current graph in the active workspace.

    This command directly modifies the graph by removing all nodes, edges, and
    adjacency information. It is executed via the application's CommandProcessor.
    
    Attributes:
        workspace_context (WorkspaceContext): Context to access the active workspace.
        args (Dict[str, Any]): Optional arguments for the command (not used here).
    """
    def __init__(self, workspace_context: WorkspaceContext, args: Dict[str, Any]):
        """
        Initialize the ClearGraphCommand.

        Args:
            workspace_context (WorkspaceContext): The context used to get the active workspace.
            args (Dict[str, Any]): Dictionary of command parameters (unused for this command).
        """
        self.workspace_context = workspace_context
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the graph clearing operation.

        Steps:
            1. Retrieve the currently active workspace from the workspace context.
            2. If no workspace is active, return a failure message.
            3. Access the current graph and clear:
                - nodes
                - edges
                - adjacency list
            4. Return a success flag and message.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the graph was cleared successfully, False otherwise.
                - message (str): Human-readable message describing the result.
        """
        workspace = self.workspace_context.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        graph.nodes.clear()
        graph.edges.clear()
        graph._adjacency_list.clear()
        return True, "Graph cleared"
        