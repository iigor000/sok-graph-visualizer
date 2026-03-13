from __future__ import annotations

import os
from typing import Dict, Any, Optional

from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.api.model.Graph import Graph

from .implementation import XmlGraphParser


class XmlDataSourceService(DataSourcePlugin):
    """
    Data source plugin that parses an arbitrary XML file and builds a Graph.

    Expected config keys
    --------------------
    file_path : str  (required)
        Absolute or relative path to the XML file.
    directed : str | bool  (optional, default True)
        Whether the resulting graph is directed.
    reference_attr : str  (optional, default "reference")
        XML attribute name used to encode cyclic back-references.
        An element carrying this attribute is treated as an edge to an
        already-existing node rather than a new node, which allows the
        parser to represent cyclic graphs.
    max_depth : int  (optional, default unlimited)
        Maximum element nesting depth to traverse.

    Usage example
    -------------
    plugin = XmlDataSourceService(config={
        "file_path": "sok_graph_visualizer/xml_datasource/data/graph.xml",
        "directed": "true",
        "reference_attr": "reference",
    })
    graph = plugin.parse()
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    def get_name(self) -> str:
        return "XML Data Source"

    def get_required_config(self) -> Dict[str, str]:
        return {
            "file_path": "Path to the XML file to parse.",
        }

    def parse(self) -> Graph:
        """
        Parse the configured XML file and return a Graph.

        Reads all parameters from ``self.config`` (set in the constructor).

        Returns
        -------
        Graph
            The fully constructed graph model.

        Raises
        ------
        ValueError
            If ``file_path`` is missing or ``max_depth`` is not an integer.
        FileNotFoundError
            If the file at ``file_path`` does not exist.
        """
        if not self.validate_config():
            missing = [
                k for k in self.get_required_config() if k not in self.config
            ]
            raise ValueError(f"Missing required config keys: {missing}")

        file_path: str = str(self.config.get("file_path", "")).strip()
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                f"XML file not found: {file_path!r}. "
                "Check the 'file_path' config value."
            )

        directed_raw = self.config.get("directed", True)
        if isinstance(directed_raw, bool):
            directed = directed_raw
        else:
            directed = str(directed_raw).strip().lower() not in ("false", "0", "no")

        reference_attr: str = (
            self.config.get("reference_attr", "reference") or "reference"
        )

        max_depth_raw = self.config.get("max_depth", None)
        max_depth: int | None = None
        if max_depth_raw not in (None, "", "null"):
            try:
                max_depth = int(max_depth_raw)
            except (TypeError, ValueError):
                raise ValueError(
                    f"'max_depth' must be an integer, got {max_depth_raw!r}."
                )

        parser = XmlGraphParser(
            directed=directed,
            max_depth=max_depth,
            reference_attr=reference_attr,
        )
        return parser.parse_file(file_path)