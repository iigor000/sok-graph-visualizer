# tests/cli/test_cli.py

import pytest

from sok_graph_visualizer.core.src.app import App
from sok_graph_visualizer.core.src.cli.cli_terminal import CLITerminal
from sok_graph_visualizer.core.src.cli.cli_parser import CLIParser
from sok_graph_visualizer.api.model.Graph import Graph


@pytest.fixture
def cli_env():
    app = App()
    parser = CLIParser()
    return app, parser


def test_create_node(cli_env):
    app, parser = cli_env

    workspace = app.workspace_service.create_workspace(name="TestWS", base_graph=Graph(graph_id="Test"))

    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    
    success, msg = app.command_processor.execute_command(cmd.name, cmd.params)
    assert success

    nodes = workspace.current_graph.nodes
    assert "1" in nodes
    assert nodes["1"].attributes.get("Name") == "Alice"


def test_edit_node(cli_env):
    app, parser = cli_env

    workspace = app.workspace_service.create_workspace(name="EditWS", base_graph=Graph(graph_id="Test"))
    
    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    app.command_processor.execute_command(cmd.name, cmd.params)

    cmd = parser.parse("edit node --id=1 --prop Age=30")
    success, msg = app.command_processor.execute_command(cmd.name, cmd.params)
    assert success

    node = workspace.current_graph.get_node("1")
    assert node.attributes.get("Name") == "Alice"
    assert node.attributes.get("Age") == 30


def test_delete_node(cli_env):
    app, parser = cli_env
    workspace = app.workspace_service.create_workspace(name="DeleteWS", base_graph=Graph(graph_id="Test"))
    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    app.command_processor.execute_command(cmd.name, cmd.params)

    cmd = parser.parse("delete node --id=1")
    success, msg = app.command_processor.execute_command(cmd.name, cmd.params)
    assert success

    nodes = workspace.current_graph.nodes
    assert "1" not in nodes


def test_create_edge(cli_env):
    app, parser = cli_env
    workspace = app.workspace_service.create_workspace(name="EdgeWS", base_graph=Graph(graph_id="Test"))

    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    app.command_processor.execute_command(cmd.name, cmd.params)
    cmd = parser.parse("create node --id=2 --prop Name=Bob")
    app.command_processor.execute_command(cmd.name, cmd.params)

    cmd = parser.parse("create edge --id=e1 --source=1 --target=2 --prop weight=5")
    success, msg = app.command_processor.execute_command(cmd.name, cmd.params)
    assert success

    edges = workspace.current_graph.edges
    assert "e1" in edges
    assert edges["e1"].source == "1"
    assert edges["e1"].target == "2"
    assert edges["e1"].attributes.get("weight") == 5


def test_clear_graph(cli_env):
    app, parser = cli_env
    workspace = app.workspace_service.create_workspace(name="ClearWS", base_graph=Graph(graph_id="Test"))

    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    app.command_processor.execute_command(cmd.name, cmd.params)
    cmd = parser.parse("create node --id=2 --prop Name=Bob")
    app.command_processor.execute_command(cmd.name, cmd.params)

    cmd = parser.parse("clear")
    success, msg = app.command_processor.execute_command(cmd.name, cmd.params)
    assert success

    assert workspace.current_graph.nodes == {}
    assert workspace.current_graph.edges == {}


def test_filter_and_search(cli_env):
    app, parser = cli_env
    workspace = app.workspace_service.create_workspace(name="FilterSearchWS", base_graph=Graph(graph_id="Test"))

    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    app.command_processor.execute_command(cmd.name, cmd.params)
    cmd = parser.parse("create node --id=2 --prop Name=Bob")
    app.command_processor.execute_command(cmd.name, cmd.params)

    cmd_filter = parser.parse("filter Name==Alice")
    success, msg = app.command_processor.execute_command(cmd_filter.name, cmd_filter.params)
    assert success

    cmd_search = parser.parse("search Alice")
    success, msg = app.command_processor.execute_command(cmd_search.name, cmd_search.params)
    assert success