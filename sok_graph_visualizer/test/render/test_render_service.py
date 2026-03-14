"""
Unit tests for RenderService class.
"""

import unittest
import sys
from pathlib import Path

# Add project root (parent of sok_graph_visualizer package) to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.core.src.use_cases.workspace_service import WorkspaceService
from sok_graph_visualizer.core.src.use_cases.render_service import RenderService


class MockVisualizer(VisualizerPlugin):
    """A minimal concrete visualizer plugin for testing."""

    def render(self, graph: Graph) -> str:
        nodes_html = "".join(
            f'<div data-node-id="{nid}"></div>' for nid in graph.nodes
        )
        return f"<html>{nodes_html}</html>"

    def get_name(self) -> str:
        return "MockVisualizer"

    def get_description(self) -> str:
        return "A mock visualizer for testing"


class TestRenderServiceInit(unittest.TestCase):
    """Tests for RenderService initialisation."""

    def setUp(self):
        self.ws = WorkspaceService()
        self.graph = Graph("g1", "Graph 1")
        self.ws.create_workspace(name="ws1", base_graph=self.graph, workspace_id="ws1")

    def test_default_visualizer_is_none(self):
        rs = RenderService(self.ws)
        self.assertIsNone(rs.visualizer)

    def test_visualizer_set_via_constructor(self):
        vis = MockVisualizer()
        rs = RenderService(self.ws, visualizer=vis)
        self.assertIs(rs.visualizer, vis)

    def test_set_visualizer(self):
        rs = RenderService(self.ws)
        vis = MockVisualizer()
        rs.set_visualizer(vis)
        self.assertIs(rs.visualizer, vis)

    def test_workspace_visualizer_is_used(self):
        rs = RenderService(self.ws)
        vis = MockVisualizer()
        workspace = self.ws.get_active_workspace()
        workspace.set_visualizer_plugin(vis)

        result = rs.render_active_workspace()

        self.assertEqual(result, '<html></html>')


class TestRenderServiceRender(unittest.TestCase):
    """Tests for render_active_workspace."""

    def setUp(self):
        self.ws = WorkspaceService()
        self.graph = Graph("g1", "Graph 1")
        self.graph.add_node(Node("A", {"name": "Node A"}))
        self.graph.add_node(Node("B", {"name": "Node B"}))
        self.graph.add_edge(Edge("e1", "A", "B", {}))
        self.ws.create_workspace(name="ws1", base_graph=self.graph, workspace_id="ws1")
        self.vis = MockVisualizer()
        self.rs = RenderService(self.ws, visualizer=self.vis)

    def test_render_returns_string(self):
        result = self.rs.render_active_workspace()
        self.assertIsInstance(result, str)

    def test_render_contains_node_ids(self):
        result = self.rs.render_active_workspace()
        self.assertIn('data-node-id="A"', result)
        self.assertIn('data-node-id="B"', result)

    def test_render_raises_without_active_workspace(self):
        self.ws.active_workspace_id = None
        with self.assertRaises(RuntimeError):
            self.rs.render_active_workspace()

    def test_render_raises_without_visualizer(self):
        rs = RenderService(self.ws)
        with self.assertRaises(RuntimeError):
            rs.render_active_workspace()

    def test_render_uses_workspace_visualizer_when_service_has_none(self):
        workspace = self.ws.get_active_workspace()
        workspace.set_visualizer_plugin(MockVisualizer())
        rs = RenderService(self.ws)

        result = rs.render_active_workspace()

        self.assertIn('data-node-id="A"', result)
        self.assertIn('data-node-id="B"', result)

    def test_render_raises_when_active_workspace_missing(self):
        self.ws.active_workspace_id = "nonexistent"
        with self.assertRaises(RuntimeError):
            self.rs.render_active_workspace()

    def test_render_empty_graph(self):
        empty_graph = Graph("empty", "Empty")
        self.ws.create_workspace(name="ws_empty", base_graph=empty_graph, workspace_id="ws_empty")
        self.ws.active_workspace_id = "ws_empty"
        result = self.rs.render_active_workspace()
        self.assertIsInstance(result, str)


class TestRenderServiceHooks(unittest.TestCase):
    """Tests for pre_render / post_render hooks."""

    def setUp(self):
        self.ws = WorkspaceService()
        self.graph = Graph("g1", "Graph 1")
        self.graph.add_node(Node("A", {}))
        self.ws.create_workspace(name="ws1", base_graph=self.graph, workspace_id="ws1")
        self.rs = RenderService(self.ws, visualizer=MockVisualizer())

    def test_pre_render_hook_called(self):
        called = []
        self.rs.register_hook("pre_render", lambda **kw: called.append(kw))
        self.rs.render_active_workspace()
        self.assertEqual(len(called), 1)
        self.assertIn("graph", called[0])
        self.assertIn("workspace", called[0])

    def test_post_render_hook_called(self):
        called = []
        self.rs.register_hook("post_render", lambda **kw: called.append(kw))
        self.rs.render_active_workspace()
        self.assertEqual(len(called), 1)
        self.assertIn("result", called[0])

    def test_post_render_hook_receives_render_result(self):
        captured = []
        self.rs.register_hook("post_render", lambda **kw: captured.append(kw["result"]))
        result = self.rs.render_active_workspace()
        self.assertEqual(captured[0], result)

    def test_multiple_hooks_all_called(self):
        calls = []
        self.rs.register_hook("pre_render", lambda **kw: calls.append("hook1"))
        self.rs.register_hook("pre_render", lambda **kw: calls.append("hook2"))
        self.rs.render_active_workspace()
        self.assertIn("hook1", calls)
        self.assertIn("hook2", calls)

    def test_hooks_not_called_on_error(self):
        called = []
        self.rs.register_hook("post_render", lambda **kw: called.append(True))
        self.rs.visualizer = None
        with self.assertRaises(RuntimeError):
            self.rs.render_active_workspace()
        self.assertEqual(called, [])


class TestRenderServiceIsConcreteVisualizer(unittest.TestCase):
    """Tests for the is_concrete_visualizer static method."""

    def test_mock_visualizer_is_concrete(self):
        self.assertTrue(RenderService.is_concrete_visualizer(MockVisualizer()))

    def test_non_plugin_object_is_not_concrete(self):
        self.assertFalse(RenderService.is_concrete_visualizer("not a plugin"))
        self.assertFalse(RenderService.is_concrete_visualizer(42))
        self.assertFalse(RenderService.is_concrete_visualizer(None))


if __name__ == "__main__":
    unittest.main()
