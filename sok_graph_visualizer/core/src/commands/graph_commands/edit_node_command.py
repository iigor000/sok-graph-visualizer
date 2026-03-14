from typing import Any, Dict, Tuple
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.api.model.Node import Node


    
class EditNodeCommand(Command):
    """
    Command to edit the attributes of an existing node in the current graph 
    of the active workspace.

    This command retrieves the active workspace, looks up the node by ID, 
    and updates its attributes with the provided key-value pairs. 
    Only attributes included in the command are modified; existing attributes 
    not mentioned remain unchanged.

    Attributes:
        workspace_context: Context used to access the active workspace.
        args (Dict[str, Any]): Dictionary containing command parameters:
            - id (str): Identifier of the node to edit.
            - properties (Dict[str, Any], optional): Key-value pairs of attributes 
              to update on the node.
    """

    def __init__(self, workspace_context, args: Dict[str, Any]):
        """
        Initialize the EditNodeCommand.

        Args:
            workspace_context: Context used to retrieve the active workspace.
            args (Dict[str, Any]): Dictionary containing the node ID and optional properties to update.
        """
        self.workspace_context = workspace_context
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the node editing operation.

        Steps:
            1. Retrieve the active workspace.
            2. If no workspace is active, return failure.
            3. Access the current graph from the workspace.
            4. Retrieve the node ID from the command arguments.
            5. Look up the node in the graph:
                - If the node does not exist, return failure.
            6. Update the node's attributes with the provided properties.
            7. Return a success flag and descriptive message.

        Returns:
            Tuple[bool, str]:
                - success (bool): True if the node was updated successfully, False otherwise.
                - message (str): Human-readable description of the result.
        """
        workspace = self.workspace_context.get_active_workspace()

        if workspace is None:
            return False, "No active workspace"

        graph = workspace.current_graph
        node_id = self.args.get("id")
        node = graph.get_node(node_id)
        if not node:
            return False, "Node not found."
        
        properties = self.args.get("properties", {})
        node.attributes.update(properties)

        return True, f"Node {node_id} updated."
    