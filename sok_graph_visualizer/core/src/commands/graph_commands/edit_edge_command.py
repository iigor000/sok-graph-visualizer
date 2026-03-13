from typing import Any, Dict, Tuple
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.use_cases.workspace_context import WorkspaceContext
from sok_graph_visualizer.api.model.Node import Node

class EditEdgeCommand(Command):
    """
    Command to edit the attributes of an existing edge in the current graph 
    of the active workspace.

    This command retrieves the active workspace, looks up the edge by ID, 
    and updates its attributes with the provided key-value pairs. 
    Only attributes provided in the command are modified; existing attributes 
    not included remain unchanged.

    Attributes:
        workspace_context (WorkspaceContext): Context to access the active workspace.
        args (Dict[str, Any]): Dictionary containing command parameters:
            - id (str): Identifier of the edge to edit.
            - properties (Dict[str, Any], optional): Key-value pairs of attributes 
              to update on the edge.
    """

    def __init__(self, workspace_context: WorkspaceContext, args: Dict[str, Any]):
        """
        Initialize the EditEdgeCommand.

        Args:
            workspace_context (WorkspaceContext): Context used to retrieve the active workspace.
            args (Dict[str, Any]): Dictionary containing the edge ID and optional properties to update.
        """
        self.workspace_context = workspace_context
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the edge editing operation.

        Steps:
            1. Retrieve the active workspace.
            2. If no workspace is active, return failure.
            3. Access the current graph from the workspace.
            4. Retrieve the edge ID from the command arguments.
            5. Look up the edge in the graph:
                - If the edge does not exist, return failure.
            6. Update the edge's attributes with the provided properties.
            7. Return success flag and a descriptive message.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the edge was updated successfully, False otherwise.
                - message (str): Human-readable description of the result.
        """
        workspace = self.workspace_context.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        edge_id = self.args.get("id")
        edge = graph.get_edge(edge_id)
        if not edge:
            return False, f"Edge {edge_id} not found"

        edge.attributes.update(self.args.get("properties", {}))

        return True, f"Edge {edge_id} updated"