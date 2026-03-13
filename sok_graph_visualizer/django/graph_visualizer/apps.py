from django.apps import AppConfig
from sok_graph_visualizer.core.src.app import App


class GraphExplorerConfig(AppConfig):
    """
    Django AppConfig for the Graph Explorer application.

    This class initializes the core application (`App`) when Django starts
    and exposes its main services to Django views.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "graph_visualizer"

    def ready(self):
        """
        Called once when Django starts.

        Here we create the core application instance which initializes:
        - WorkspaceService
        - WorkspaceContext
        - CommandProcessor
        - registered commands
        """
        self.core_app = App()

    @property
    def command_processor(self):
        """Return the CommandProcessor instance."""
        return self.core_app.command_processor

    @property
    def graph_query_service(self):
        """Return the GraphQueryService instance."""
        return self.core_app.graph_query_service

    @property
    def plugin_manager(self):
        """Return the PluginManager instance."""
        return self.core_app.plugin_manager

    def execute_command(self, command_name: str, args: dict):
        """Execute a command through the command processor."""
        return self.core_app.execute_command(command_name, args)

    def get_active_workspace(self):
        """Get the currently active workspace."""
        return self.core_app.get_active_workspace()

    def get_workspace(self, workspace_id: str):
        """Get a workspace by ID."""
        return self.core_app.get_workspace(workspace_id)

    def list_workspaces(self):
        """Get a list of all workspaces."""
        return self.core_app.list_workspaces()