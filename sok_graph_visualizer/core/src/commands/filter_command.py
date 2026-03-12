from typing import Any, Dict, Tuple
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.commands.command_names import CommandNames
from sok_graph_visualizer.core.src.graph_query.graph_query_service import GraphQueryService
from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager


class FilterCommand(Command) :
    """
    Command that applies a filter expression to the graph in the active workspace.
    The command retrieves the active workspace, applies the filter through
    GraphQueryService, and stores the resulting graph as a new operation
    in the workspace history.
    """
    def __init__(self, workspace_manager : WorkspaceManager, graph_query_service : GraphQueryService, args : Dict[str, Any]) -> None:
        """
        Initialize the FilterCommand.

        Args:
            workspace_manager: Manager used to access the active workspace.
            graph_query_service: Service responsible for executing graph queries.
            args: Dictionary containing command parameters (expects 'expression').
        """
        self.workspace_manager = workspace_manager
        self.graph_query_service = graph_query_service
        self.args = args

    def execute(self) -> Tuple[bool, str]:
        """
        Execute the filter operation.

        Returns:
            Tuple[bool, str]:
                - success flag
                - message describing the result
        """
        active_workspace : Workspace | None = self.workspace_manager.get_active_workspace()
        if active_workspace is None:
            return False, f"No active workspace"
        
        expression = self.args.get("expression")
        if not expression or not isinstance(expression, str):
            return False, "Filter expression is required."
        
        try:
            filtered_graph = self.graph_query_service.filter(active_workspace.current_graph, expression)

            active_workspace.apply_operation(
                new_graph=filtered_graph,
                operation_type=CommandNames.FILTER,
                plugin_name=None,
                parameters={"expression": expression},
                description=f"Filter applied: {expression}"
            )

            return True, f"Filter applied : {expression}"
        
        except ValueError as error:
            return False, str(error)
        
        except Exception as exception:
            return False, f"Failed to apply filter {str(exception)}"

