from abc import ABC, abstractmethod
from ..model.Graph import Graph

class VisualizerPlugin(ABC):
    """
    Abstract base class for visualizer plugins.
    
    Visualizer plugins are responsible for:
    1. Accepting a Graph object from the platform
    2. Generating HTML/CSS/JavaScript code to render the graph
    3. Returning the HTML string to the platform for display
    
    Each plugin implements a specific visualization style
    (e.g., simple circles, detailed blocks).
    """
    
    @abstractmethod
    def render(self, graph: Graph) -> str:
        """
        Render a graph as HTML.
        
        This method should:
        1. Iterate over nodes and edges in the graph
        2. Generate HTML elements (divs, SVG, canvas, etc.)
        3. Include inline CSS or reference external stylesheets
        4. Optionally include JavaScript for interactivity
        5. Return the complete HTML string
        
        Args:
            graph: The Graph object to visualize
            
        Returns:
            str: HTML string representing the graph visualization
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the human-readable name of this plugin.
        
        Returns:
            str: Plugin name (e.g., "Simple Visualizer", "Block Visualizer")
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get a description of the visualization style.
        
        Returns:
            str: Description of how this plugin renders graphs
        """
        pass
    
    def get_required_scripts(self) -> list[str]:
        """
        Get a list of JavaScript libraries required by this visualizer.
        
        Returns:
            List of script URLs or paths (e.g., ["https://d3js.org/d3.v7.min.js"])
        """
        return []
    
    def get_required_styles(self) -> list[str]:
        """
        Get a list of CSS files required by this visualizer.
        
        Returns:
            List of stylesheet URLs or paths
        """
        return []
