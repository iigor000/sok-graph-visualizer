from pathlib import Path
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin
from sok_graph_visualizer.rdf_datasource.src.services import RDFParserService


class RDFDataSourcePlugin(DataSourcePlugin):
    """
    RDFDataSourcePlugin is a concrete implementation of the DataSourcePlugin
    abstract base class.

    This plugin is responsible for:
    - Loading RDF data from a file (e.g., Turtle, RDF/XML)
    - Validating required configuration parameters
    - Delegating parsing logic to RDFParserService
    - Returning a populated Graph object compatible with the platform

    Expected configuration parameters:
        - file_path (str): Path to the RDF file
        - format (str): RDF format (e.g., "turtle", "xml")
    """

    def get_name(self) -> str:
        """
        Returns the human-readable name of this plugin.

        Returns:
            str: Name of the data source plugin.
        """
        return "RDF Data Source"

    def get_required_config(self):
        """
        Specifies the required configuration parameters for this plugin.

        Returns:
            Dict[str, str]: Dictionary where keys are configuration parameter
                            names and values are their descriptions.
        """
        return {
            "file_path": "Path to RDF file",
            "format": "RDF format (e.g. turtle, xml)"
        }

    def parse(self) -> Graph:
        """
        Parses the RDF file defined in the configuration and constructs
        a Graph object.

        Workflow:
            1. Validates configuration parameters.
            2. Verifies that the RDF file exists.
            3. Delegates RDF parsing to RDFParserService.
            4. Returns a populated Graph instance.

        Returns:
            Graph: Graph object populated with nodes and edges
                   extracted from the RDF file.

        Raises:
            ValueError: If required configuration parameters are missing.
            FileNotFoundError: If the specified RDF file does not exist.
        """
        if not self.validate_config():
            raise ValueError("Missing required configuration parameters")

        file_path = self.config["file_path"]
        format = self.config["format"]

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"RDF file not found {file_path}")

        parser = RDFParserService()
        return parser.parse(file_path, format)