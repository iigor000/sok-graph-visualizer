from typing import Any, Dict, Tuple
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.use_cases.workspace_context import WorkspaceContext

class CreateEdgeCommand(Command):
    """
    Command to create a new edge in the current graph of the active workspace.

    This command retrieves the active workspace, constructs an Edge object
    using the provided parameters, and adds it to the current graph.
    
    Attributes:
        workspace_context (WorkspaceContext): Context to access the active workspace.
        args (Dict[str, Any]): Dictionary containing command parameters such as:
            - id (str): Unique identifier for the new edge.
            - source (str): Node ID of the edge's source.
            - target (str): Node ID of the edge's target.
            - properties (Dict[str, Any], optional): Edge attributes.
    """

    def __init__(self, workspace_context: WorkspaceContext, args: Dict[str, Any]):
        """
        Initialize the CreateEdgeCommand.

        Args:
            workspace_context (WorkspaceContext): The context used to get the active workspace.
            args (Dict[str, Any]): Dictionary of parameters for the new edge.
        """
        self.workspace_context = workspace_context
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the edge creation operation.

        Steps:
            1. Retrieve the active workspace from the workspace context.
            2. If no workspace is active, return a failure message.
            3. Access the current graph.
            4. Retrieve edge parameters from `args`:
                - id
                - source
                - target
                - properties
            5. Create a new Edge object and add it to the graph.
            6. Return a success flag and a message with the new edge ID.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the edge was created successfully, False otherwise.
                - message (str): Human-readable message describing the result.
        """
        workspace = self.workspace_context.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        properties = self.args.get("properties", {})
        edge = Edge(
            edge_id=self.args.get("id"),
            source=self.args.get("source"),
            target=self.args.get("target"),
            attributes=self.args.get("properties", {})
        )
        graph.add_edge(edge)

        return True, f"Edge {edge.edge_id} created"