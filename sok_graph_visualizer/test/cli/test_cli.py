# tests/cli/test_cli.py

import pytest

from sok_graph_visualizer.core.src.app import App
from sok_graph_visualizer.platform.cli.cli_terminal import CLITerminal
from sok_graph_visualizer.platform.cli.cli_parser import CLIParser
from sok_graph_visualizer.platform.cli.cli_executor import CLIExecutor
from sok_graph_visualizer.api.model.Graph import Graph


@pytest.fixture
def cli_env():
    app = App()
    parser = CLIParser()
    executor = CLIExecutor(app)
    return app, parser, executor


def test_create_node(cli_env):
    app, parser, executor = cli_env

    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="TestWS")

    cmd = parser.parse("create node --id=1 --prop Name=Alice")
    executor.execute(cmd)

    nodes = workspace.current_graph.nodes
    assert "1" in nodes
    assert nodes["1"].attributes.get("Name") == "Alice"


def test_edit_node(cli_env):
    app, parser, executor = cli_env

    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="EditWS")
    
    executor.execute(parser.parse("create node --id=1 --prop Name=Alice"))

    executor.execute(parser.parse("edit node --id=1 --prop Age=30"))
    node = workspace.current_graph.get_node("1")
    assert node.attributes.get("Name") == "Alice"
    assert node.attributes.get("Age") == "30"


def test_delete_node(cli_env):
    app, parser, executor = cli_env
    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="DeleteWS")
    executor.execute(parser.parse("create node --id=1 --prop Name=Alice"))
    executor.execute(parser.parse("delete node --id=1"))

    nodes = workspace.current_graph.nodes
    assert "1" not in nodes


def test_create_edge(cli_env):
    app, parser, executor = cli_env
    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="EdgeWS")

    executor.execute(parser.parse("create node --id=1 --prop Name=Alice"))
    executor.execute(parser.parse("create node --id=2 --prop Name=Bob"))

    executor.execute(parser.parse("create edge --id=e1 --source=1 --target=2 --prop weight=5"))

    edges = workspace.current_graph.edges
    assert "e1" in edges
    assert edges["e1"].source == "1"
    assert edges["e1"].target == "2"
    assert edges["e1"].attributes.get("weight") == "5"


def test_clear_graph(cli_env):
    app, parser, executor = cli_env
    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="ClearWS")

    executor.execute(parser.parse("create node --id=1 --prop Name=Alice"))
    executor.execute(parser.parse("create node --id=2 --prop Name=Bob"))
    executor.execute(parser.parse("clear"))

    assert workspace.current_graph.nodes == {}
    assert workspace.current_graph.edges == {}


def test_filter_and_search(cli_env):
    app, parser, executor = cli_env
    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="FilterSearchWS")

    executor.execute(parser.parse("create node --id=1 --prop Name=Alice"))
    executor.execute(parser.parse("create node --id=2 --prop Name=Bob"))

    cmd_filter = parser.parse("filter Name=Alice")
    executor.execute(cmd_filter)

    cmd_search = parser.parse("search Alice")
    executor.execute(cmd_search)


def test_undo_redo(cli_env):
    app, parser, executor = cli_env
    workspace = app.workspace_manager.create_workspace(base_graph=Graph(), name="UndoRedoWS")

    executor.execute(parser.parse("create node --id=1 --prop Name=Alice"))
    executor.execute(parser.parse("create node --id=2 --prop Name=Bob"))

    assert workspace.can_undo()
    app.workspace_manager.undo()
    nodes = workspace.current_graph.nodes
    assert "2" not in nodes
    assert "1" in nodes

    app.workspace_manager.redo()
    nodes = workspace.current_graph.nodes
    assert "2" in nodes