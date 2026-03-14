from typing import Any, Dict, Tuple
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.use_cases.workspace_context import WorkspaceContext
from sok_graph_visualizer.api.model.Node import Node

class CreateNodeCommand(Command):
    """
    Command to create a new node in the current graph of the active workspace.

    This command retrieves the active workspace, constructs a Node object
    using the provided parameters, and adds it to the current graph.

    Attributes:
        workspace_context (WorkspaceContext): Context to access the active workspace.
        args (Dict[str, Any]): Dictionary containing command parameters such as:
            - id (str): Unique identifier for the new node.
            - properties (Dict[str, Any], optional): Node attributes.
    """

    def __init__(self, workspace_context: WorkspaceContext, args: Dict[str, Any]):
        """
        Initialize the CreateNodeCommand.

        Args:
            workspace_context (WorkspaceContext): Context to retrieve the active workspace.
            args (Dict[str, Any]): Dictionary of parameters for the new node.
        """
        self.workspace_context = workspace_context
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the node creation operation.

        Steps:
            1. Retrieve the active workspace from the workspace context.
            2. If no workspace is active, return a failure message.
            3. Access the current graph.
            4. Retrieve node parameters from `args`:
                - id
                - properties
            5. Validate that a node id is provided.
            6. Create a new Node object and add it to the graph.
            7. Return a success flag and a message with the new node ID.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the node was created successfully, False otherwise.
                - message (str): Human-readable message describing the result.
        """
        workspace = self.workspace_context.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        node_id = self.args.get("id")
        if not node_id:
            return False, "Node id is required"
        properties = self.args.get("properties", {})
        node = Node(node_id=node_id, attributes=properties)

        graph.add_node(node)

        return True, f"Node {node_id} created"