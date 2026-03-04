
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.core.src.use_cases.render_service import RenderService


class App():
    """
    Main application class for the graph visualizer platform.
    Initializes the workspace manager and handles interactions between the UI and the workspace.

    """

    def __init__(self):
        """
        Initialize workspace manager and plugins.
        """
        self.workspace_manager = WorkspaceManager()
        self.render_service = RenderService(self.workspace_manager)
        self.visualizer : VisualizerPlugin = None
        self.data_source_plugin : DataSourcePlugin = None

    def render_graph(self):
        """
        Render the graph of the active workspace using the render service.
        """
        if self.visualizer is None:
            raise RuntimeError("No visualizer plugin selected")
        return self.render_service.render_active_workspace()