import unittest
from pathlib import Path
import sys
from typing import Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.core.src.commands.workspace_commands import CreateWorkspaceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import DeleteWorkspaceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import RefreshDataSourceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import SelectVisualizerCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import SelectWorkspaceCommand
from sok_graph_visualizer.core.src.commands.workspace_commands import UpdateWorkspaceCommand
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager


class CountingDataSourcePlugin(DataSourcePlugin):
    def parse(self) -> Graph:
        suffix = self.config.get("suffix", "A")
        graph = Graph(graph_id=f"graph_{suffix}", name=f"Graph {suffix}")
        graph.add_node(Node(f"N{suffix}", {"name": f"Node {suffix}"}))
        return graph

    def get_name(self) -> str:
        return "Counting Data Source"

    def get_required_config(self) -> Dict[str, str]:
        return {}


class BasicVisualizerPlugin(VisualizerPlugin):
    def render(self, graph: Graph) -> str:
        return f"<html>{graph.graph_id}</html>"

    def get_name(self) -> str:
        return "Basic Visualizer"

    def get_description(self) -> str:
        return "Visualizer used in workspace command tests"


class FakePluginManager:
    def instantiate_data_source(self, name: str, **kwargs):
        if name != "counting_ds":
            raise ValueError(f"ds plugin '{name}' not found")
        return CountingDataSourcePlugin(**kwargs)

    def instantiate_visualizer(self, name: str, **kwargs):
        if name != "basic_vis":
            raise ValueError(f"dv plugin '{name}' not found")
        return BasicVisualizerPlugin()


class TestWorkspaceCommands(unittest.TestCase):
    def setUp(self):
        self.workspace_manager = WorkspaceManager()
        self.plugin_manager = FakePluginManager()

        initial_graph = Graph(graph_id="initial", name="Initial")
        initial_graph.add_node(Node("N0", {"name": "Node 0"}))
        self.workspace_manager.create_workspace(initial_graph, workspace_id="ws0", name="Workspace 0")

    def test_select_workspace_command(self):
        second_graph = Graph(graph_id="second", name="Second")
        second_graph.add_node(Node("N1", {"name": "Node 1"}))
        self.workspace_manager.create_workspace(second_graph, workspace_id="ws1", name="Workspace 1", set_active=False)

        command = SelectWorkspaceCommand(self.workspace_manager, {"workspace_id": "ws1"})

        success, message = command.execute()

        self.assertTrue(success)
        self.assertEqual(message, "Selected workspace Workspace 1")
        self.assertEqual(self.workspace_manager.active_workspace_id, "ws1")

    def test_create_workspace_command(self):
        command = CreateWorkspaceCommand(
            self.workspace_manager,
            self.plugin_manager,
            {
                "workspace_id": "ws2",
                "name": "Workspace 2",
                "data_source_id": "counting_ds",
                "config": {"suffix": "B"},
                "visualizer_id": "basic_vis",
            },
        )

        success, message = command.execute()
        workspace = self.workspace_manager.get_workspace("ws2")

        self.assertTrue(success)
        self.assertEqual(message, "Created workspace Workspace 2")
        self.assertEqual(workspace.current_graph.graph_id, "graph_B")
        self.assertIsInstance(workspace.data_source_plugin, CountingDataSourcePlugin)
        self.assertIsInstance(workspace.visualizer_plugin, BasicVisualizerPlugin)
        self.assertEqual(self.workspace_manager.active_workspace_id, "ws2")

    def test_update_workspace_command(self):
        workspace = self.workspace_manager.get_workspace("ws0")
        workspace.apply_operation(workspace.current_graph, "test")

        command = UpdateWorkspaceCommand(
            self.workspace_manager,
            self.plugin_manager,
            {
                "workspace_id": "ws0",
                "name": "Workspace Updated",
                "data_source_id": "counting_ds",
                "config": {"suffix": "C"},
                "visualizer_id": "basic_vis",
            },
        )

        success, message = command.execute()

        self.assertTrue(success)
        self.assertEqual(message, "Updated workspace Workspace Updated")
        self.assertEqual(workspace.name, "Workspace Updated")
        self.assertEqual(workspace.current_graph.graph_id, "graph_C")
        self.assertEqual(len(workspace.operation_history), 0)
        self.assertIsInstance(workspace.data_source_plugin, CountingDataSourcePlugin)
        self.assertIsInstance(workspace.visualizer_plugin, BasicVisualizerPlugin)

    def test_delete_workspace_command(self):
        second_graph = Graph(graph_id="second", name="Second")
        second_graph.add_node(Node("N1", {"name": "Node 1"}))
        self.workspace_manager.create_workspace(second_graph, workspace_id="ws1", name="Workspace 1", set_active=False)

        command = DeleteWorkspaceCommand(self.workspace_manager, {"workspace_id": "ws1"})

        success, message = command.execute()

        self.assertTrue(success)
        self.assertEqual(message, "Successfully removed the workspace")
        self.assertIsNone(self.workspace_manager.get_workspace("ws1"))

    def test_delete_workspace_command_rejects_last_workspace(self):
        command = DeleteWorkspaceCommand(self.workspace_manager, {"workspace_id": "ws0"})

        success, message = command.execute()

        self.assertFalse(success)
        self.assertEqual(message, "There must be at least one workspace")

    def test_select_visualizer_command(self):
        command = SelectVisualizerCommand(
            self.workspace_manager,
            self.plugin_manager,
            {"visualizer_id": "basic_vis"},
        )

        success, message = command.execute()
        workspace = self.workspace_manager.get_active_workspace()

        self.assertTrue(success)
        self.assertEqual(message, "Selected Basic Visualizer as visualizer")
        self.assertIsInstance(workspace.visualizer_plugin, BasicVisualizerPlugin)

    def test_refresh_data_source_command(self):
        workspace = self.workspace_manager.get_active_workspace()
        workspace.set_data_source_plugin(CountingDataSourcePlugin(config={"suffix": "R1"}))
        workspace.apply_operation(workspace.current_graph, "test")

        command = RefreshDataSourceCommand(self.workspace_manager, {"config": {"suffix": "R2"}})

        success, message = command.execute()

        self.assertTrue(success)
        self.assertEqual(message, "Successfully reloaded the data")
        self.assertEqual(workspace.current_graph.graph_id, "graph_R2")
        self.assertEqual(len(workspace.operation_history), 0)


if __name__ == "__main__":
    unittest.main()