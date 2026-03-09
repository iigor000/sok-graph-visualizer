from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node
from rdflib import Graph as RDFGraph, Literal, URIRef

from sok_graph_visualizer.rdf_datasource.src.utils import convert_literal


class RDFParserService:
    """
    RDFParserService is responsible for parsing RDF files and converting
    RDF triples into the internal Graph model used by the platform.

    This service:
    - Loads RDF data using rdflib
    - Iterates over RDF triples (subject, predicate, object)
    - Creates Node and Edge objects
    - Converts RDF literals into Python-native types
    - Returns a populated Graph instance

    The resulting Graph:
    - Contains nodes representing RDF resources
    - Contains edges for object-property relationships (URIRef)
    - Stores literal values as node attributes
    """

    def _normalize(self, uri):
        """
        Extracts the local name from a URI.

        This method removes namespace prefixes by returning the last
        segment of the URI (after '#' or '/').

        Examples:
            http://example.org/person1 → person1
            http://xmlns.com/foaf/0.1/name → name
            http://www.w3.org/2001/XMLSchema#date → date

        Args:
            uri: rdflib URIRef or value convertible to string.

        Returns:
            str: Normalized local identifier.
        """
        uri_str = str(uri)

        if "#" in uri_str:
            return uri_str.split("#")[-1]
        if "/" in uri_str:
            return uri_str.rstrip("/").split("/")[-1]
        return uri_str

    def parse(self, file_path: str, rdf_format: str) -> Graph:
        """
        Parses an RDF file and converts it into the platform's Graph model.

        Workflow:
            1. Loads RDF data using rdflib.
            2. Creates an empty directed Graph.
            3. Iterates over RDF triples.
            4. Creates nodes for subjects and object resources.
            5. Creates edges for object relationships (URIRef).
            6. Stores literal values as node attributes.

        Args:
            file_path (str): Path to the RDF file.
            rdf_format (str): RDF serialization format
                              (e.g., "turtle", "xml").

        Returns:
            Graph: A populated Graph object representing RDF data.
        """

        rdf_graph = RDFGraph()
        rdf_graph.parse(file_path, format=rdf_format)

        graph = Graph(
            graph_id="rdf_graph",
            name="RDF Graph",
            directed=True
        )

        for subject, predicate, obj in rdf_graph:
            subject_id = self._normalize(subject)
            predicate_name = self._normalize(predicate)

            # Ensure subject node exists
            if subject_id not in graph.nodes:
                graph.add_node(Node(subject_id))

            # Case 1: Object is a URI (relationship → create edge)
            if isinstance(obj, URIRef):
                obj_id = self._normalize(obj)

                if obj_id not in graph.nodes:
                    graph.add_node(Node(obj_id))

                edge_id = f"{subject_id}_{predicate_name}_{obj_id}"

                graph.add_edge(Edge(
                    edge_id=edge_id,
                    source=subject_id,
                    target=obj_id,
                    attributes={"predicate": predicate_name}
                ))

            # Case 2: Object is a literal (attribute → attach to node)
            elif isinstance(obj, Literal):
                value = convert_literal(obj)
                graph.nodes[subject_id].set_attribute(
                    predicate_name,
                    value
                )

        return graph