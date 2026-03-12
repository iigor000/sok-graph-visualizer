
from sok_graph_visualizer.core.src.commands.command_names import CommandNames
from sok_graph_visualizer.core.src.commands.command_processor import CommandProcessor
from sok_graph_visualizer.core.src.commands.filter_command import FilterCommand
from sok_graph_visualizer.core.src.commands.search_command import SearchCommand
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.core.src.use_cases.render_service import RenderService


class App():
    """
    Main application class for the graph visualizer platform.
    Initializes the workspace manager, register commands and handles interactions between the UI and the workspace.

    """

    def __init__(self):
        """
        Initialize workspace manager, command processor and plugins.
        """
        self.workspace_manager = WorkspaceManager()
        self.render_service = RenderService(self.workspace_manager)
        self.visualizer : VisualizerPlugin = None
        self.data_source_plugin : DataSourcePlugin = None
        self.command_processor = CommandProcessor()

        self.register_commands()

    def register_commands(self) -> None:
        """
        Register application commands using factories.
        """
        self.command_processor.register_command(
            CommandNames.FILTER,
            lambda args: FilterCommand(
                workspace_manager=self.workspace_manager,
                graph_query_service=self.graph_query_service,
                args=args
            )
        )

        self.command_processor.register_command(
            CommandNames.SEARCH,
            lambda args: SearchCommand(
                workspace_manager=self.workspace_manager,
                graph_query_service=self.graph_query_service,
                args=args
            )
        )
    def render_graph(self):
        """
        Render the graph of the active workspace using the render service.
        """
        if self.visualizer is None:
            raise RuntimeError("No visualizer plugin selected")
        return self.render_service.render_active_workspace()