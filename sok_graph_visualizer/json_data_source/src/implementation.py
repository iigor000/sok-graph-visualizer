import json
from typing import Dict
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.json_data_source.src.service import JsonGraphParserService

class JsonDataSourcePlugin(DataSourcePlugin):
    """
    Plugin for parsing JSON files and converting them into a Graph structure.

    Responsibilities:
    - Accepts a configuration dictionary with the path to the JSON file.
    - Instantiates JsonGraphParserService.
    - Parses the JSON and constructs a Graph object.

    Returns:
    - Graph: A populated graph with nodes and edges derived from the JSON structure.
    """

    def get_name(self) -> str:
        return "JSON Data Source"

    def get_required_config(self) -> Dict[str, str]:
        return { "file_path": "Path to the JSON file" }

    def parse(self) -> Graph:

        if not self.validate_config():
            raise ValueError("Missing configuration")

        file_path = self.config.get("file_path")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            directed = True
            graph_id = "json_graph"
        else:
            directed = data.get("directed", True)
            graph_id = data.get("graph_id", "json_graph")

        graph = Graph(
            graph_id=graph_id,
            directed=directed
        )

        service = JsonGraphParserService()

        return service.parse(data, graph)