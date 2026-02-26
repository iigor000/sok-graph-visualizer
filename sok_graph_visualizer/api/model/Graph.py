from .Edge import Edge
from .Node import Node
from typing import Dict, Optional, Set, List
from copy import deepcopy


class Graph:
    """
    Represents a graph data structure.
    
    A graph is a collection of nodes and edges. It supports:
    - Directed and undirected graphs
    - Cyclic and acyclic graphs
    - Adding/removing nodes and edges
    - Querying and filtering operations
    
    Attributes:
        graph_id (str): Unique identifier for the graph
        name (str): Human-readable name for the graph
        directed (bool): Whether the graph is directed
        nodes (Dict[str, Node]): Dictionary mapping node IDs to Node objects
        edges (Dict[str, Edge]): Dictionary mapping edge IDs to Edge objects
    """
    
    def __init__(self, graph_id: str, name: str = "", directed: bool = True):
        """
        Initialize a Graph.
        
        Args:
            graph_id: Unique identifier for the graph
            name: Human-readable name (optional)
            directed: Whether the graph is directed (default: True)
        """
        self.graph_id = graph_id
        self.name = name or graph_id
        self.directed = directed
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self._adjacency_list: Dict[str, Set[str]] = {}  # For efficient traversal
    
    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.
        
        Args:
            node: The Node object to add
            
        Raises:
            ValueError: If a node with the same ID already exists
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node with id '{node.node_id}' already exists")
        self.nodes[node.node_id] = node
        self._adjacency_list[node.node_id] = set()
    
    def remove_node(self, node_id: str) -> None:
        """
        Remove a node from the graph.
        
        Args:
            node_id: ID of the node to remove
            
        Raises:
            ValueError: If the node has connected edges
        """
        if node_id not in self.nodes:
            return
        
        # Check if node has any connected edges
        connected_edges = self.get_node_edges(node_id)
        if connected_edges:
            raise ValueError(
                f"Cannot remove node '{node_id}' because it has {len(connected_edges)} "
                f"connected edge(s). Remove edges first."
            )
        
        del self.nodes[node_id]
        del self._adjacency_list[node_id]
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by its ID."""
        return self.nodes.get(node_id)
    
    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the graph.
        
        Args:
            edge: The Edge object to add
            
        Raises:
            ValueError: If source or target node doesn't exist, or edge ID already exists
        """
        if edge.source not in self.nodes:
            raise ValueError(f"Source node '{edge.source}' does not exist")
        if edge.target not in self.nodes:
            raise ValueError(f"Target node '{edge.target}' does not exist")
        if edge.edge_id in self.edges:
            raise ValueError(f"Edge with id '{edge.edge_id}' already exists")
        
        self.edges[edge.edge_id] = edge
        self._adjacency_list[edge.source].add(edge.target)
        
        # For undirected graphs, add reverse connection
        if not self.directed:
            self._adjacency_list[edge.target].add(edge.source)
    
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from the graph."""
        if edge_id not in self.edges:
            return
        
        edge = self.edges[edge_id]
        self._adjacency_list[edge.source].discard(edge.target)
        
        if not self.directed:
            self._adjacency_list[edge.target].discard(edge.source)
        
        del self.edges[edge_id]
    
    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by its ID."""
        return self.edges.get(edge_id)
    
    def get_node_edges(self, node_id: str) -> List[Edge]:
        """
        Get all edges connected to a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of edges connected to the node
        """
        connected_edges = []
        for edge in self.edges.values():
            if edge.source == node_id or edge.target == node_id:
                connected_edges.append(edge)
        return connected_edges
    
    def get_neighbors(self, node_id: str) -> Set[str]:
        """
        Get IDs of all neighboring nodes.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Set of neighboring node IDs
        """
        return self._adjacency_list.get(node_id, set()).copy()
    
    def is_cyclic(self) -> bool:
        """
        Check if the graph contains cycles.
        
        Returns:
            True if the graph has at least one cycle, False otherwise
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor in self._adjacency_list.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle_util(node_id):
                    return True
        
        return False
    
    def get_subgraph(self, node_ids: Set[str]) -> 'Graph':
        """
        Create a subgraph containing only the specified nodes and their connecting edges.
        
        Args:
            node_ids: Set of node IDs to include in the subgraph
            
        Returns:
            A new Graph object representing the subgraph
        """
        subgraph = Graph(
            graph_id=f"{self.graph_id}_subgraph",
            name=f"{self.name} (filtered)",
            directed=self.directed
        )
        
        # Add nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                subgraph.add_node(deepcopy(node))
        
        # Add edges where both source and target are in the subgraph
        for edge in self.edges.values():
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(deepcopy(edge))
        
        return subgraph
    
    def __repr__(self) -> str:
        return f"Graph(id={self.graph_id}, nodes={len(self.nodes)}, edges={len(self.edges)})"
