"""
Unit tests for Workspace and WorkspaceService classes.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.use_cases.workspace_service import WorkspaceService
from sok_graph_visualizer.core.src.workspace.operation import Operation


class TestOperation(unittest.TestCase):
    """Test cases for Operation class."""
    
    def test_operation_creation(self):
        """Test creating an operation."""
        op = Operation(
            operation_type="add_node",
            parameters={"node_id": "A"},
            description="Add node A"
        )
        
        self.assertEqual(op.operation_type, "add_node")
        self.assertEqual(op.parameters["node_id"], "A")
        self.assertEqual(op.description, "Add node A")
        self.assertIsNotNone(op.operation_id)
        self.assertIsNotNone(op.timestamp)
        self.assertFalse(hasattr(op, "plugin_name"))
    
    def test_operation_without_optional_fields(self):
        """Test creating an operation with only the required field."""
        op = Operation(operation_type="manual_edit")
        
        self.assertEqual(op.operation_type, "manual_edit")
        self.assertEqual(op.parameters, {})
        self.assertEqual(op.description, "manual_edit")
        self.assertFalse(hasattr(op, "plugin_name"))


class TestWorkspace(unittest.TestCase):
    """Test cases for Workspace class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test graph
        self.graph = Graph(graph_id="test_graph", name="Test Graph", directed=True)
        self.graph.add_node(Node("A", {"name": "Node A"}))
        self.graph.add_node(Node("B", {"name": "Node B"}))
        self.graph.add_node(Node("C", {"name": "Node C"}))
        self.graph.add_edge(Edge("e1", "A", "B", {}))
        self.graph.add_edge(Edge("e2", "B", "C", {}))
    
    def test_workspace_creation(self):
        """Test creating a workspace."""
        data_source_plugin = object()
        visualizer_plugin = object()
        ws = Workspace(
            workspace_id="ws1",
            base_graph=self.graph,
            name="Test Workspace",
            data_source_plugin=data_source_plugin,
            visualizer_plugin=visualizer_plugin,
            metadata={"author": "TestUser"}
        )
        
        self.assertEqual(ws.workspace_id, "ws1")
        self.assertEqual(ws.name, "Test Workspace")
        self.assertEqual(len(ws.base_graph.nodes), 3)
        self.assertEqual(len(ws.current_graph.nodes), 3)
        self.assertIs(ws.data_source_plugin, data_source_plugin)
        self.assertIs(ws.visualizer_plugin, visualizer_plugin)
        self.assertEqual(ws.metadata["author"], "TestUser")
        self.assertIsNone(ws.selected_node_id)
        self.assertEqual(len(ws.operation_history), 0)
        self.assertEqual(ws.current_operation_index, -1)
    
    def test_workspace_default_name(self):
        """Test workspace with default name."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        self.assertEqual(ws.name, "ws1")
    
    def test_apply_operation(self):
        """Test applying an operation to workspace."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Create a modified graph
        modified_graph = Graph(graph_id="modified", directed=True)
        modified_graph.add_node(Node("A", {"name": "Node A"}))
        modified_graph.add_node(Node("B", {"name": "Node B"}))
        modified_graph.add_node(Node("C", {"name": "Node C"}))
        modified_graph.add_node(Node("D", {"name": "Node D"}))
        modified_graph.add_edge(Edge("e1", "A", "B", {}))
        modified_graph.add_edge(Edge("e2", "B", "C", {}))
        
        # Apply operation
        ws.apply_operation(
            new_graph=modified_graph,
            operation_type="add_node",
            parameters={"node_id": "D"},
            description="Added node D"
        )
        
        self.assertEqual(len(ws.operation_history), 1)
        self.assertEqual(ws.current_operation_index, 0)
        self.assertEqual(len(ws.current_graph.nodes), 4)
        self.assertIn("D", ws.current_graph.nodes)
    
    def test_multiple_operations(self):
        """Test applying multiple operations."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Operation 1: Add node D
        graph1 = Graph(graph_id="g1", directed=True)
        for node_id in ["A", "B", "C", "D"]:
            graph1.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        graph1.add_edge(Edge("e1", "A", "B", {}))
        graph1.add_edge(Edge("e2", "B", "C", {}))
        
        ws.apply_operation(graph1, "add_node", parameters={"node_id": "D"})
        
        # Operation 2: Add edge
        graph2 = Graph(graph_id="g2", directed=True)
        for node_id in ["A", "B", "C", "D"]:
            graph2.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        graph2.add_edge(Edge("e1", "A", "B", {}))
        graph2.add_edge(Edge("e2", "B", "C", {}))
        graph2.add_edge(Edge("e3", "C", "D", {}))
        
        ws.apply_operation(graph2, "add_edge", parameters={"edge_id": "e3"})
        
        self.assertEqual(len(ws.operation_history), 2)
        self.assertEqual(ws.current_operation_index, 1)
        self.assertEqual(len(ws.current_graph.edges), 3)
    
    def test_undo_operation(self):
        """Test undoing an operation."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Add an operation
        modified_graph = Graph(graph_id="modified", directed=True)
        for node_id in ["A", "B", "C", "D"]:
            modified_graph.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        
        ws.apply_operation(modified_graph, "add_node")
        
        self.assertEqual(ws.current_operation_index, 0)
        self.assertTrue(ws.can_undo())
        
        # Undo
        result = ws.undo()
        self.assertTrue(result)
        self.assertEqual(ws.current_operation_index, -1)
        self.assertFalse(ws.can_undo())
    
    def test_undo_at_base_state(self):
        """Test undo when already at base state."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        result = ws.undo()
        self.assertFalse(result)
        self.assertEqual(ws.current_operation_index, -1)
    
    def test_redo_operation(self):
        """Test redoing an operation."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Add operation and then undo
        modified_graph = Graph(graph_id="modified", directed=True)
        for node_id in ["A", "B", "C", "D"]:
            modified_graph.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        
        ws.apply_operation(modified_graph, "add_node")
        ws.undo()
        
        self.assertEqual(ws.current_operation_index, -1)
        self.assertTrue(ws.can_redo())
        
        # Redo
        result = ws.redo()
        self.assertTrue(result)
        self.assertEqual(ws.current_operation_index, 0)
        self.assertFalse(ws.can_redo())
    
    def test_redo_at_end_of_history(self):
        """Test redo when at end of history."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        result = ws.redo()
        self.assertFalse(result)
    
    def test_apply_operation_truncates_redo_history(self):
        """Test that applying operation after undo truncates redo history."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Apply two operations
        graph1 = Graph(graph_id="g1", directed=True)
        for node_id in ["A", "B", "C", "D"]:
            graph1.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        ws.apply_operation(graph1, "op1")
        
        graph2 = Graph(graph_id="g2", directed=True)
        for node_id in ["A", "B", "C", "D", "E"]:
            graph2.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        ws.apply_operation(graph2, "op2")
        
        # Undo once
        ws.undo()
        self.assertEqual(len(ws.operation_history), 2)
        self.assertEqual(ws.current_operation_index, 0)
        
        # Apply new operation - should truncate op2
        graph3 = Graph(graph_id="g3", directed=True)
        for node_id in ["A", "B", "C", "D", "F"]:
            graph3.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        ws.apply_operation(graph3, "op3")
        
        self.assertEqual(len(ws.operation_history), 2)  # op1 and op3
        self.assertEqual(ws.current_operation_index, 1)
        self.assertFalse(ws.can_redo())
    
    def test_reset_workspace(self):
        """Test resetting workspace to base state."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Apply some operations
        graph1 = Graph(graph_id="g1", directed=True)
        for node_id in ["A", "B", "C", "D"]:
            graph1.add_node(Node(node_id, {"name": f"Node {node_id}"}))
        ws.apply_operation(graph1, "op1")
        ws.apply_operation(graph1, "op2")
        
        ws.set_selected_node("A")
        
        # Reset
        ws.reset()
        
        self.assertEqual(len(ws.operation_history), 0)
        self.assertEqual(ws.current_operation_index, -1)
        self.assertEqual(len(ws.current_graph.nodes), 3)  # Back to original
        self.assertIsNone(ws.selected_node_id)
    
    def test_selected_node(self):
        """Test selecting and getting nodes."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Select a node
        ws.set_selected_node("A")
        self.assertEqual(ws.selected_node_id, "A")
        
        selected_node = ws.get_selected_node()
        self.assertIsNotNone(selected_node)
        self.assertEqual(selected_node.node_id, "A")
        
        # Deselect
        ws.set_selected_node(None)
        self.assertIsNone(ws.selected_node_id)
        self.assertIsNone(ws.get_selected_node())
    
    def test_select_invalid_node(self):
        """Test selecting a node that doesn't exist."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        with self.assertRaises(ValueError) as context:
            ws.set_selected_node("Z")
        
        self.assertIn("does not exist", str(context.exception))
    
    def test_metadata_operations(self):
        """Test metadata getter and setter."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # Set metadata
        ws.update_metadata("plugin_config", {"param1": "value1"})
        ws.update_metadata("last_action", "transform")
        
        # Get metadata
        self.assertEqual(ws.get_metadata("plugin_config"), {"param1": "value1"})
        self.assertEqual(ws.get_metadata("last_action"), "transform")
        self.assertIsNone(ws.get_metadata("nonexistent"))
        self.assertEqual(ws.get_metadata("nonexistent", "default"), "default")
    
    def test_get_current_operation(self):
        """Test getting the current operation."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        
        # No operations yet
        self.assertIsNone(ws.get_current_operation())
        
        # Add operation
        graph1 = Graph(graph_id="g1", directed=True)
        ws.apply_operation(graph1, "test_op")
        
        current_op = ws.get_current_operation()
        self.assertIsNotNone(current_op)
        self.assertEqual(current_op.operation_type, "test_op")
        self.assertFalse(hasattr(current_op, "plugin_name"))

    def test_workspace_plugin_setters(self):
        """Test assigning plugins directly to a workspace."""
        ws = Workspace(workspace_id="ws1", base_graph=self.graph)
        data_source_plugin = object()
        visualizer_plugin = object()

        ws.set_data_source_plugin(data_source_plugin)
        ws.set_visualizer_plugin(visualizer_plugin)

        self.assertIs(ws.data_source_plugin, data_source_plugin)
        self.assertIs(ws.visualizer_plugin, visualizer_plugin)


class TestWorkspaceService(unittest.TestCase):
    """Test cases for WorkspaceService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.graph = Graph(graph_id="test_graph", name="Test Graph", directed=True)
        self.graph.add_node(Node("A", {"name": "Node A"}))
        self.graph.add_node(Node("B", {"name": "Node B"}))
        self.graph.add_edge(Edge("e1", "A", "B", {}))
    
    def test_manager_creation(self):
        """Test creating a workspace service."""
        service = WorkspaceService()
        
        self.assertEqual(len(service.workspaces), 0)
        self.assertIsNone(service.active_workspace_id)
    
    def test_create_workspace(self):
        """Test creating a workspace through service."""
        service = WorkspaceService()
        data_source_plugin = object()
        visualizer_plugin = object()
        
        ws = service.create_workspace(
            name="Test Workspace",
            base_graph=self.graph,
            workspace_id="ws1",
            data_source_plugin=data_source_plugin,
            visualizer_plugin=visualizer_plugin
        )
        
        self.assertEqual(ws.workspace_id, "ws1")
        self.assertIs(ws.data_source_plugin, data_source_plugin)
        self.assertIs(ws.visualizer_plugin, visualizer_plugin)
        self.assertEqual(len(service.workspaces), 1)
        self.assertEqual(service.active_workspace_id, "ws1")
    
    def test_create_workspace_auto_id(self):
        """Test creating workspace with auto-generated ID."""
        service = WorkspaceService()
        
        ws = service.create_workspace(name="Workspace", base_graph=self.graph)
        
        self.assertIsNotNone(ws.workspace_id)
        self.assertIn(ws.workspace_id, service.workspaces)
    
    def test_create_workspace_duplicate_id(self):
        """Test creating workspace with duplicate ID."""
        service = WorkspaceService()
        service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        with self.assertRaises(ValueError) as context:
            service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_create_workspace_not_active(self):
        """Test creating workspace without setting it active."""
        service = WorkspaceService()
        
        ws1 = service.create_workspace(name="Workspace 1", base_graph=self.graph, workspace_id="ws1")
        ws2 = service.create_workspace(name="Workspace 2", base_graph=self.graph, workspace_id="ws2", set_active=False)
        
        self.assertEqual(service.active_workspace_id, "ws1")
        self.assertEqual(len(service.workspaces), 2)
    
    def test_delete_workspace(self):
        """Test deleting a workspace."""
        service = WorkspaceService()
        service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        result = service.remove_workspace("ws1")
        
        self.assertTrue(result)
        self.assertEqual(len(service.workspaces), 0)
        self.assertIsNone(service.active_workspace_id)
    
    def test_delete_nonexistent_workspace(self):
        """Test deleting a workspace that doesn't exist."""
        service = WorkspaceService()
        
        result = service.remove_workspace("ws999")
        self.assertFalse(result)
    
    def test_delete_active_workspace_switches_to_another(self):
        """Test that deleting active workspace switches to another."""
        service = WorkspaceService()
        service.create_workspace(name="Workspace 1", base_graph=self.graph, workspace_id="ws1")
        service.create_workspace(name="Workspace 2", base_graph=self.graph, workspace_id="ws2")
        
        service.set_active_workspace("ws1")
        service.remove_workspace("ws1")
        
        self.assertEqual(len(service.workspaces), 1)
        self.assertEqual(service.active_workspace_id, "ws2")
    
    def test_get_workspace(self):
        """Test getting a workspace by ID."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        retrieved = service.get_workspace("ws1")
        self.assertEqual(retrieved, ws)
        
        not_found = service.get_workspace("ws999")
        self.assertIsNone(not_found)
    
    def test_get_active_workspace(self):
        """Test getting the active workspace."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        active = service.get_active_workspace()
        self.assertEqual(active, ws)
    
    def test_get_active_workspace_none(self):
        """Test getting active workspace when none is active."""
        service = WorkspaceService()
        
        active = service.get_active_workspace()
        self.assertIsNone(active)
    
    def test_set_active_workspace(self):
        """Test setting the active workspace."""
        service = WorkspaceService()
        service.create_workspace(name="Workspace 1", base_graph=self.graph, workspace_id="ws1")
        service.create_workspace(name="Workspace 2", base_graph=self.graph, workspace_id="ws2")
        
        result = service.set_active_workspace("ws2")
        self.assertTrue(result)
        self.assertEqual(service.active_workspace_id, "ws2")
    
    def test_set_active_workspace_invalid(self):
        """Test setting active workspace to invalid ID."""
        service = WorkspaceService()
        
        result = service.set_active_workspace("ws999")
        self.assertFalse(result)
    
    def test_list_workspaces(self):
        """Test listing all workspaces."""
        service = WorkspaceService()
        ws1 = service.create_workspace(name="Workspace 1", base_graph=self.graph, workspace_id="ws1")
        ws2 = service.create_workspace(name="Workspace 2", base_graph=self.graph, workspace_id="ws2")
        
        all_workspaces = service.get_workspaces()
        self.assertEqual(len(all_workspaces), 2)
        self.assertIn(ws1, all_workspaces)
        self.assertIn(ws2, all_workspaces)
    
    def test_reset_workspace(self):
        """Test resetting a workspace through service."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        # Apply an operation
        modified_graph = Graph(graph_id="modified", directed=True)
        modified_graph.add_node(Node("A", {"name": "Node A"}))
        modified_graph.add_node(Node("B", {"name": "Node B"}))
        modified_graph.add_node(Node("C", {"name": "Node C"}))
        ws.apply_operation(modified_graph, "add_node")
        
        # Reset via service
        result = service.reset_workspace("ws1")
        self.assertTrue(result)
        self.assertEqual(len(ws.operation_history), 0)
    
    def test_reset_active_workspace(self):
        """Test resetting active workspace without specifying ID."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        # Apply operation
        modified_graph = Graph(graph_id="modified", directed=True)
        ws.apply_operation(modified_graph, "test")
        
        # Reset without specifying ID
        result = service.reset_workspace()
        self.assertTrue(result)
        self.assertEqual(len(ws.operation_history), 0)
    
    def test_reset_nonexistent_workspace(self):
        """Test resetting workspace that doesn't exist."""
        service = WorkspaceService()
        
        result = service.reset_workspace("ws999")
        self.assertFalse(result)
    
    def test_undo_through_manager(self):
        """Test undo through manager."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        # Apply operation
        modified_graph = Graph(graph_id="modified", directed=True)
        ws.apply_operation(modified_graph, "test")
        
        # Undo via service
        result = service.undo("ws1")
        self.assertTrue(result)
        self.assertEqual(ws.current_operation_index, -1)
    
    def test_undo_active_workspace(self):
        """Test undo on active workspace."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph)
        
        modified_graph = Graph(graph_id="modified", directed=True)
        ws.apply_operation(modified_graph, "test")
        
        result = service.undo()  # No workspace_id specified
        self.assertTrue(result)
    
    def test_redo_through_manager(self):
        """Test redo through manager."""
        service = WorkspaceService()
        ws = service.create_workspace(name="Workspace", base_graph=self.graph, workspace_id="ws1")
        
        modified_graph = Graph(graph_id="modified", directed=True)
        ws.apply_operation(modified_graph, "test")
        service.undo("ws1")
        
        result = service.redo("ws1")
        self.assertTrue(result)
        self.assertEqual(ws.current_operation_index, 0)
    
    def test_clear_all(self):
        """Test clearing all workspaces."""
        service = WorkspaceService()
        service.create_workspace(name="Workspace 1", base_graph=self.graph, workspace_id="ws1")
        service.create_workspace(name="Workspace 2", base_graph=self.graph, workspace_id="ws2")
        
        service.clear_all()
        
        self.assertEqual(len(service.workspaces), 0)
        self.assertIsNone(service.active_workspace_id)


if __name__ == "__main__":
    unittest.main()
