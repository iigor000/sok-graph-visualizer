"""
Example usage of SimpleVisualizer.
This script creates a simple graph and visualizes it.
"""

import sys
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "simple_visualizer" / "src"))

from api.model.Graph import Graph
from api.model.abstract.Node import Node
from api.model.abstract.Edge import Edge
from simple_visualizer import SimpleVisualizer


def create_sample_graph():
    """Creates a sample graph with several nodes and edges."""
    # Create graph
    graph = Graph(graph_id="example_graph", name="Example Graph", directed=True)
    
    # Add nodes
    node1 = Node("A", {"name": "Node A", "label": "A"})
    node2 = Node("B", {"name": "Node B", "label": "B"})
    node3 = Node("C", {"name": "Node C", "label": "C"})
    node4 = Node("D", {"name": "Node D", "label": "D"})
    node5 = Node("E", {"name": "Node E", "label": "E"})
    node6 = Node("F", {"name": "Node F", "label": "F"})
    node7 = Node("G", {"name": "Node G", "label": "G"})
    node8 = Node("H", {"name": "Node H", "label": "H"})
    node9 = Node("I", {"name": "Node I", "label": "I"})
    node10 = Node("J", {"name": "Node J", "label": "J"})
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_node(node4)
    graph.add_node(node5)
    graph.add_node(node6)
    graph.add_node(node7)
    graph.add_node(node8)
    graph.add_node(node9)
    graph.add_node(node10)
    
    # Add edges - creating a more complex network
    # Central hub pattern
    edge1 = Edge("e1", "A", "B", {"weight": 1})
    edge2 = Edge("e2", "A", "C", {"weight": 2})
    edge3 = Edge("e3", "A", "D", {"weight": 3})
    edge4 = Edge("e4", "A", "E", {"weight": 4})
    
    # Secondary connections
    edge5 = Edge("e5", "B", "F", {"weight": 5})
    edge6 = Edge("e6", "C", "G", {"weight": 6})
    edge7 = Edge("e7", "D", "H", {"weight": 7})
    edge8 = Edge("e8", "E", "I", {"weight": 8})
    
    # Cross connections
    edge9 = Edge("e9", "F", "G", {"weight": 9})
    edge10 = Edge("e10", "G", "H", {"weight": 10})
    edge11 = Edge("e11", "H", "I", {"weight": 11})
    edge12 = Edge("e12", "I", "F", {"weight": 12})
    
    # Connection to J
    edge13 = Edge("e13", "F", "J", {"weight": 13})
    edge14 = Edge("e14", "J", "A", {"weight": 14})
    
    # Bidirectional edges
    edge15 = Edge("e15", "B", "C", {"weight": 15})
    edge16 = Edge("e16", "C", "B", {"weight": 16})
    
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    graph.add_edge(edge3)
    graph.add_edge(edge4)
    graph.add_edge(edge5)
    graph.add_edge(edge6)
    graph.add_edge(edge7)
    graph.add_edge(edge8)
    graph.add_edge(edge9)
    graph.add_edge(edge10)
    graph.add_edge(edge11)
    graph.add_edge(edge12)
    graph.add_edge(edge13)
    graph.add_edge(edge14)
    graph.add_edge(edge15)
    graph.add_edge(edge16)
    
    return graph


def main():
    """Main program."""
    # Create graph
    print("Creating sample graph...")
    graph = create_sample_graph()
    
    # Create visualizer
    print("Initializing SimpleVisualizer...")
    visualizer = SimpleVisualizer()
    
    # Generate HTML
    print("Generating HTML visualization...")
    html_output = visualizer.render(graph)
    
    # Save to HTML file
    output_file = "graph_visualization.html"
    with open(output_file, "w", encoding="utf-8") as f:
        # Add basic HTML wrapper with D3.js library
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        #main {
            width: 100vw;
            height: 100vh;
        }
    </style>
</head>
<body>
    <div id="main"></div>
""")
        f.write(html_output)
        f.write("""
</body>
</html>
""")
    
    print(f"✓ Visualization saved to: {output_file}")
    print(f"  Open the file in your browser to view the graph.")


if __name__ == "__main__":
    main()
