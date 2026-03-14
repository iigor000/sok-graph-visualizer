
from sok_graph_visualizer.core.src.commands.command_names import CommandNames
from sok_graph_visualizer.core.src.commands.command_processor import CommandProcessor
from sok_graph_visualizer.core.src.commands.filter_command import FilterCommand
from sok_graph_visualizer.core.src.commands.graph_commands.clear_graph_command import ClearGraphCommand
from sok_graph_visualizer.core.src.commands.graph_commands.create_edge_command import CreateEdgeCommand
from sok_graph_visualizer.core.src.commands.graph_commands.create_node_command import CreateNodeCommand
from sok_graph_visualizer.core.src.commands.graph_commands.delete_edge_command import DeleteEdgeCommand
from sok_graph_visualizer.core.src.commands.graph_commands.delete_node_command import DeleteNodeCommand
from sok_graph_visualizer.core.src.commands.graph_commands.edit_edge_command import EditEdgeCommand
from sok_graph_visualizer.core.src.commands.graph_commands.edit_node_command import EditNodeCommand
from sok_graph_visualizer.core.src.commands.search_command import SearchCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import CreateWorkspaceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import DeleteWorkspaceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import RefreshDataSourceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import SelectVisualizerCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import SelectWorkspaceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import UpdateWorkspaceCommand
from sok_graph_visualizer.core.src.graph_query.graph_query_service import GraphQueryService
from sok_graph_visualizer.core.src.use_cases.plugin_recognition import PluginManager
from sok_graph_visualizer.core.src.use_cases.workspace_service import WorkspaceService
from sok_graph_visualizer.core.src.use_cases.workspace_context import WorkspaceContext
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin


class App():
    """
    Main application class for the graph visualizer platform.
    Initializes the workspace service and context, register commands and handles interactions between the UI and the workspace.

    """

    def __init__(self):
        """
        Initialize workspace service and context, command processor and plugins.
        """
        self.workspace_service = WorkspaceService()
        self.workspace_context = WorkspaceContext(self.workspace_service)
        self.visualizer : VisualizerPlugin = None
        self.data_source_plugin : DataSourcePlugin = None
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.command_processor = CommandProcessor()
        self.graph_query_service = GraphQueryService()

        self.register_commands()

    def register_commands(self) -> None:
        """
        Register application commands using factories.
        """
        self.command_processor.register_command(
            CommandNames.FILTER,
            lambda args: FilterCommand(
                workspace_context=self.workspace_context,
                graph_query_service=self.graph_query_service,
                args=args
            )
        )

        self.command_processor.register_command(
            CommandNames.SEARCH,
            lambda args: SearchCommand(
                workspace_context=self.workspace_context,
                graph_query_service=self.graph_query_service,
                args=args
            )
        )

        # CREATE NODE
        self.command_processor.register_command(
            CommandNames.CREATE_NODE,
            lambda args: CreateNodeCommand(self.workspace_context, args)
        )

        # EDIT NODE
        self.command_processor.register_command(
            CommandNames.EDIT_NODE,
            lambda args: EditNodeCommand(self.workspace_context, args)
        )

        # DELETE NODE
        self.command_processor.register_command(
            CommandNames.DELETE_NODE,
            lambda args: DeleteNodeCommand(self.workspace_context, args)
        )

        # CREATE EDGE
        self.command_processor.register_command(
            CommandNames.CREATE_EDGE,
            lambda args: CreateEdgeCommand(self.workspace_context, args)
        )

        # EDIT EDGE
        self.command_processor.register_command(
            CommandNames.EDIT_EDGE,
            lambda args: EditEdgeCommand(self.workspace_context, args)
        )

        # DELETE EDGE
        self.command_processor.register_command(
            CommandNames.DELETE_EDGE,
            lambda args: DeleteEdgeCommand(self.workspace_context, args)
        )

        # CLEAR GRAPH
        self.command_processor.register_command(
            CommandNames.CLEAR_GRAPH,
            lambda args: ClearGraphCommand(self.workspace_context, args)
        )

        # SELECT WORKSPACE
        self.command_processor.register_command(
            CommandNames.SELECT_WORKSPACE,
            lambda args: SelectWorkspaceCommand(self.workspace_context, args)
        )

        # CREATE WORKSPACE
        self.command_processor.register_command(
            CommandNames.CREATE_WORKSPACE,
            lambda args: CreateWorkspaceCommand(self.workspace_service, self.workspace_context, self.plugin_manager, args)
        )

        # UPDATE WORKSPACE
        self.command_processor.register_command(
            CommandNames.UPDATE_WORKSPACE,
            lambda args: UpdateWorkspaceCommand(self.workspace_service, self.workspace_context, self.plugin_manager, args)
        )

        # DELETE WORKSPACE
        self.command_processor.register_command(
            CommandNames.DELETE_WORKSPACE,
            lambda args: DeleteWorkspaceCommand(self.workspace_context, args)
        )

        # SELECT VISUALIZER
        self.command_processor.register_command(
            CommandNames.SELECT_VISUALIZER,
            lambda args: SelectVisualizerCommand(self.workspace_context, self.plugin_manager, args)
        )

        # REFRESH DATA SOURCE
        self.command_processor.register_command(
            CommandNames.REFRESH_DATA_SOURCE,
            lambda args: RefreshDataSourceCommand(self.workspace_context, args)
        )