from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sok_graph_visualizer.api.model.Graph import Graph

class DataSourcePlugin(ABC):
    """
    Abstract base class for data source plugins.
    
    Data source plugins are responsible for:
    1. Accepting configuration parameters (e.g., file paths, API keys)
    2. Parsing data from various sources (JSON, XML, CSV, etc.)
    3. Constructing a Graph object from the parsed data
    
    Each plugin must implement the parse() method to convert raw data
    into a graph structure.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin with configuration parameters.
        
        Args:
            config: Dictionary containing plugin-specific configuration.
                    For example: {"file_path": "/path/to/data.json"}
                    or {"api_url": "https://api.example.com", "api_key": "..."}
        """
        self.config = config or {}
    
    @abstractmethod
    def parse(self) -> Graph:
        """
        Parse the data source and construct a Graph.
        
        This method should:
        1. Read/fetch data from the configured source
        2. Parse the data format (JSON, XML, CSV, etc.)
        3. Create Node and Edge objects
        4. Build and return a Graph object
        
        Returns:
            Graph: A populated graph structure
            
        Raises:
            ValueError: If configuration is invalid or data cannot be parsed
            FileNotFoundError: If a file path is invalid
            ConnectionError: If a remote resource cannot be accessed
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the human-readable name of this plugin.
        
        Returns:
            str: Plugin name (e.g., "JSON Data Source", "XML Parser")
        """
        pass
    
    @abstractmethod
    def get_required_config(self) -> Dict[str, str]:
        """
        Get the required configuration parameters for this plugin.
        
        Returns:
            Dict mapping parameter names to their descriptions.
            Example: {"file_path": "Path to the JSON file"}
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate that all required configuration parameters are present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required = self.get_required_config()
        for param in required.keys():
            if param not in self.config:
                return False
        return True