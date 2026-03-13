from copy import deepcopy
from typing import Any, Dict, Optional, Tuple

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.core.src.commands.command import Command
from sok_graph_visualizer.core.src.use_cases.plugin_recognition import PluginManager
from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager


def _replace_workspace_graph(workspace: Workspace, graph: Graph) -> None:
    workspace.base_graph = deepcopy(graph)
    workspace.reset()


class SelectWorkspaceCommand(Command):
    def __init__(self, workspace_manager: WorkspaceManager, args: Dict[str, Any]):
        self.workspace_manager = workspace_manager
        workspace_id = args.get("workspace_id")
        self.workspace_id = str(workspace_id) if workspace_id is not None else None

    def execute(self) -> Tuple[bool, str]:
        if not self.workspace_id:
            return False, "Missing 'workspace_id'"

        if not self.workspace_manager.set_active_workspace(self.workspace_id):
            return False, f"Workspace not found: {self.workspace_id}"

        workspace = self.workspace_manager.get_active_workspace()
        return True, f"Selected workspace {workspace.name}"


class CreateWorkspaceCommand(Command):
    def __init__(self, workspace_manager: WorkspaceManager, plugin_manager: PluginManager, args: Dict[str, Any]):
        self.workspace_manager = workspace_manager
        self.plugin_manager = plugin_manager
        self.workspace_id = args.get("workspace_id")
        self.name = args.get("name")
        self.data_source_id = args.get("data_source_id")
        self.data_source_config = args.get("config", {})
        self.visualizer_id = args.get("visualizer_id")
        self.visualizer_config = args.get("visualizer_config", {})

    def execute(self) -> Tuple[bool, str]:
        if not self.name:
            return False, "Missing 'name'"
        if not self.data_source_id:
            return False, "Missing 'data_source_id'"

        try:
            data_source_plugin = self.plugin_manager.instantiate_data_source(
                self.data_source_id,
                config=self.data_source_config,
            )
            base_graph = data_source_plugin.parse()
            visualizer_plugin = self._instantiate_visualizer()

            workspace = self.workspace_manager.create_workspace(
                base_graph=base_graph,
                workspace_id=str(self.workspace_id) if self.workspace_id is not None else None,
                name=self.name,
                data_source_plugin=data_source_plugin,
                visualizer_plugin=visualizer_plugin,
            )
            return True, f"Created workspace {workspace.name}"
        except ValueError as error:
            return False, str(error)
        except Exception as error:
            return False, f"Failed to create workspace: {str(error)}"

    def _instantiate_visualizer(self) -> Optional[VisualizerPlugin]:
        if not self.visualizer_id:
            return None
        return self.plugin_manager.instantiate_visualizer(
            self.visualizer_id,
            **self.visualizer_config,
        )


class UpdateWorkspaceCommand(Command):
    def __init__(self, workspace_manager: WorkspaceManager, plugin_manager: PluginManager, args: Dict[str, Any]):
        self.workspace_manager = workspace_manager
        self.plugin_manager = plugin_manager
        workspace_id = args.get("workspace_id")
        self.workspace_id = str(workspace_id) if workspace_id is not None else None
        self.name = args.get("name")
        self.data_source_id = args.get("data_source_id")
        self.data_source_config = args.get("config", {})
        self.visualizer_id = args.get("visualizer_id")
        self.visualizer_config = args.get("visualizer_config", {})

    def execute(self) -> Tuple[bool, str]:
        if not self.workspace_id:
            return False, "Missing 'workspace_id'"
        if not self.name:
            return False, "Missing 'name'"
        if not self.data_source_id:
            return False, "Missing 'data_source_id'"

        workspace = self.workspace_manager.get_workspace(self.workspace_id)
        if workspace is None:
            return False, f"Workspace not found: {self.workspace_id}"

        try:
            data_source_plugin = self.plugin_manager.instantiate_data_source(
                self.data_source_id,
                config=self.data_source_config,
            )
            graph = data_source_plugin.parse()
            visualizer_plugin = self._resolve_visualizer(workspace)

            workspace.name = self.name
            workspace.set_data_source_plugin(data_source_plugin)
            workspace.set_visualizer_plugin(visualizer_plugin)
            _replace_workspace_graph(workspace, graph)
            self.workspace_manager.set_active_workspace(self.workspace_id)

            return True, f"Updated workspace {workspace.name}"
        except ValueError as error:
            return False, str(error)
        except Exception as error:
            return False, f"Failed to update workspace: {str(error)}"

    def _resolve_visualizer(self, workspace: Workspace) -> Optional[VisualizerPlugin]:
        if not self.visualizer_id:
            return workspace.visualizer_plugin
        return self.plugin_manager.instantiate_visualizer(
            self.visualizer_id,
            **self.visualizer_config,
        )


class DeleteWorkspaceCommand(Command):
    def __init__(self, workspace_manager: WorkspaceManager, args: Dict[str, Any]) -> None:
        self.workspace_manager = workspace_manager
        workspace_id = args.get("workspace_id")
        self.workspace_id = str(workspace_id) if workspace_id is not None else None

    def execute(self) -> Tuple[bool, str]:
        if not self.workspace_id:
            return False, "Missing 'workspace_id'"

        if self.workspace_manager.get_workspace(self.workspace_id) is None:
            return False, f"Workspace not found: {self.workspace_id}"

        if len(self.workspace_manager.workspaces) <= 1:
            return False, "There must be at least one workspace"

        try:
            self.workspace_manager.delete_workspace(self.workspace_id)
            return True, "Successfully removed the workspace"
        except Exception as error:
            return False, f"Failed to delete workspace: {str(error)}"


class SelectVisualizerCommand(Command):
    def __init__(self, workspace_manager: WorkspaceManager, plugin_manager: PluginManager, args: Dict[str, Any]) -> None:
        self.workspace_manager = workspace_manager
        self.plugin_manager = plugin_manager
        self.visualizer_id = args.get("visualizer_id")
        self.visualizer_config = args.get("visualizer_config", {})
        workspace_id = args.get("workspace_id")
        self.workspace_id = str(workspace_id) if workspace_id is not None else None

    def execute(self) -> Tuple[bool, str]:
        if not self.visualizer_id:
            return False, "No visualizer id provided"

        workspace = self.workspace_manager.get_workspace(self.workspace_id) if self.workspace_id else self.workspace_manager.get_active_workspace()
        if workspace is None:
            return False, "No active workspace"

        try:
            visualizer = self.plugin_manager.instantiate_visualizer(
                self.visualizer_id,
                **self.visualizer_config,
            )
            workspace.set_visualizer_plugin(visualizer)
            return True, f"Selected {visualizer.get_name()} as visualizer"
        except ValueError:
            return False, f"Unknown visualizer: {self.visualizer_id}"
        except Exception as error:
            return False, f"Failed to select visualizer: {str(error)}"


class RefreshDataSourceCommand(Command):
    def __init__(self, workspace_manager: WorkspaceManager, args: Optional[Dict[str, Any]] = None) -> None:
        self.workspace_manager = workspace_manager
        self.args = args or {}
        workspace_id = self.args.get("workspace_id")
        self.workspace_id = str(workspace_id) if workspace_id is not None else None
        self.config = self.args.get("config")

    def execute(self) -> Tuple[bool, str]:
        workspace = self.workspace_manager.get_workspace(self.workspace_id) if self.workspace_id else self.workspace_manager.get_active_workspace()
        if workspace is None:
            return False, "No active workspace"

        data_source_plugin = workspace.data_source_plugin
        if data_source_plugin is None:
            return False, "No data source selected"

        try:
            if self.config is not None:
                data_source_plugin.config = self.config
            graph = data_source_plugin.parse()
            _replace_workspace_graph(workspace, graph)
            return True, "Successfully reloaded the data"
        except Exception as error:
            return False, f"Failed to refresh data source: {str(error)}"