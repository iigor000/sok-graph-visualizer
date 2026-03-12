from django.apps import AppConfig
from sok_graph_visualizer.core.src.app import App


class GraphExplorerConfig(AppConfig):
    """
    Django AppConfig for the Graph Explorer application.

    This class initializes the core application (`App`) when Django starts
    and exposes its main services (workspace manager, render service,
    command processor, etc.) to Django views.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "graph_visualizer"

    def ready(self):
        """
        Called once when Django starts.

        Here we create the core application instance which initializes:
        - WorkspaceManager
        - RenderService
        - CommandProcessor
        - registered commands
        """
        self.core_app = App()

    @property
    def workspace_manager(self):
        """Return the WorkspaceManager instance."""
        return self.core_app.workspace_manager

    @property
    def render_service(self):
        """Return the RenderService instance."""
        return self.core_app.render_service

    @property
    def command_processor(self):
        """Return the CommandProcessor instance."""
        return self.core_app.command_processor

    @property
    def graph_query_service(self):
        """Return the GraphQueryService instance."""
        return self.core_app.graph_query_service