from typing import Any, Dict, Tuple

from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.commands.command_names import CommandNames
from sok_graph_visualizer.core.src.graph_query.graph_query_service import GraphQueryService
from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager


class SearchCommand(Command) :
    """
    Command that performs a search operation on the graph in the active workspace.

    The command retrieves the active workspace, executes the search through
    GraphQueryService, and stores the resulting graph as a new operation
    in the workspace history.
    """
    def __init__(self, workspace_manager : WorkspaceManager, graph_query_service : GraphQueryService, args : Dict[str, Any]) -> None:
        """
        Initialize the SearchCommand.

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
        Execute the search operation.

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
            return False, "Search expression is required."
        
        try:
            searched_graph = self.graph_query_service.search(active_workspace.current_graph, expression)

            active_workspace.apply_operation(
                new_graph=searched_graph,
                operation_type=CommandNames.SEARCH,
                parameters={"expression": expression},
                description=f"Search applied: {expression}"

            )

            return True, f"Search applied : {expression}"
        
        except ValueError as error:
            return False, str(error)
        
        except Exception as exception:
            return False, f"Failed to apply search {str(exception)}"

