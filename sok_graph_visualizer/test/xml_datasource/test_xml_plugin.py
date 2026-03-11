import os
import pytest

from sok_graph_visualizer.xml_datasource.src.service import XmlDataSourceService

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "xml_datasource", "data")
TRANSIT_XML = os.path.normpath(os.path.join(DATA_DIR, "graph.xml"))


def test_xml_plugin_parse_basic():
    """
    Checks that the plugin parses the XML file and returns a non-empty graph.
    """
    plugin = XmlDataSourceService(config={"file_path": TRANSIT_XML})
    graph = plugin.parse()

    assert graph is not None
    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0

    print("\n===== GRAPH STRUCTURE =====")
    print(f"Nodes count: {len(graph.nodes)}")
    print(f"Edges count: {len(graph.edges)}")

    print("\nNodes:")
    for node_id, node in graph.nodes.items():
        print(f"  {node_id} -> {node.attributes}")

    print("\nEdges:")
    for edge_id, edge in graph.edges.items():
        print(f"  {edge_id}: {edge.source} -> {edge.target} | attrs={edge.attributes}")


def test_xml_plugin_cyclic():
    """
    The transit network contains bidirectional connections and interchange
    references, so the resulting graph must be cyclic.
    """
    plugin = XmlDataSourceService(config={"file_path": TRANSIT_XML})
    graph = plugin.parse()

    assert graph.is_cyclic(), "Transit network graph should be cyclic"


def test_xml_plugin_directed_false():
    """
    When directed=False the graph should be undirected.
    """
    plugin = XmlDataSourceService(config={
        "file_path": TRANSIT_XML,
        "directed": "false",
    })
    graph = plugin.parse()

    assert graph.directed is False


def test_xml_plugin_missing_file():
    """
    A FileNotFoundError should be raised when the file does not exist.
    """
    plugin = XmlDataSourceService(config={"file_path": "/nonexistent/path/file.xml"})
    with pytest.raises(FileNotFoundError):
        plugin.parse()


def test_xml_plugin_missing_config():
    """
    A ValueError should be raised when file_path is not provided.
    """
    plugin = XmlDataSourceService(config={})
    with pytest.raises(ValueError):
        plugin.parse()


def test_xml_plugin_get_name():
    plugin = XmlDataSourceService(config={})
    assert plugin.get_name() == "XML Data Source"


def test_xml_plugin_get_required_config():
    plugin = XmlDataSourceService(config={})
    required = plugin.get_required_config()
    assert "file_path" in required


def test_xml_plugin_node_attributes():
    """
    Nodes should have typed attributes – integers must not be stored as strings.
    """
    plugin = XmlDataSourceService(config={"file_path": TRANSIT_XML})
    graph = plugin.parse()

    # Find a station node (has platforms and daily_passengers as integers)
    station_nodes = [
        node for node in graph.nodes.values()
        if node.attributes.get("_tag") == "station"
    ]
    assert len(station_nodes) > 0, "Expected at least one station node"

    station = station_nodes[0]
    # platforms and daily_passengers should be parsed as int, not str
    if "platforms" in station.attributes:
        assert isinstance(station.attributes["platforms"], int), (
            f"Expected int for 'platforms', got {type(station.attributes['platforms'])}"
        )
    if "daily_passengers" in station.attributes:
        assert isinstance(station.attributes["daily_passengers"], int), (
            f"Expected int for 'daily_passengers', got {type(station.attributes['daily_passengers'])}"
        )


def test_xml_plugin_custom_reference_attr():
    """
    Passing a reference_attr that does not appear in the file means no
    cyclic references will be resolved – the graph may still parse correctly
    but will treat reference elements as regular nodes.
    """
    plugin = XmlDataSourceService(config={
        "file_path": TRANSIT_XML,
        "reference_attr": "__nonexistent__",
    })
    graph = plugin.parse()

    # Graph should still be constructed without errors
    assert graph is not None
    assert len(graph.nodes) > 0