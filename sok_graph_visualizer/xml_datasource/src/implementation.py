from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any
from lxml import etree
from sok_graph_visualizer.api.model.Edge import Edge
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node

_DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%Y/%m/%d",
)

def _coerce(raw):
    """Attempt to coerce a raw string to the most specific Python type."""
    raw = raw.strip()

    # integer
    try:
        return int(raw)
    except ValueError:
        pass

    # float
    try:
        return float(raw)
    except ValueError:
        pass

    # date
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass

    return raw


def _node_id(element, tree):
    """stable, unique ID derived from the element's XPath in the document."""
    return tree.getpath(element)

class XmlGraphParser:
    """
    Parses an XML document into a Graph object.

    Params:
    directed:
        Whether edges should be directed (default True).
    max_depth:
        Maximum recursion depth for element traversal.  ``None`` means
        unlimited.
    reference_attr:
        Name of the XML attribute used to express cyclic references.
        Defaults to "reference".
    """

    def __init__(self,directed = True,max_depth = None,reference_attr = "reference"):
        self.directed = directed
        self.max_depth = max_depth
        self.reference_attr = reference_attr
        self._graph: Graph | None = None
        self._tree: etree._ElementTree | None = None
        # element xpath is node_id  (used for cycle detection / reference resolution)
        self._xpath_to_id: dict[str, str] = {}
        self._edge_counter: int = 0
        self._pending_refs: list[tuple[str, str, str]] = [] # source node id, ref xpath and tag


    def parse_file(self, path):
        """Parse an XML file at *path* and return a Graph."""
        parser = etree.XMLParser(remove_comments=True, recover=True)
        tree: etree._ElementTree = etree.parse(path, parser)
        return self._parse_tree(tree)

    def parse_string(self, xml_string: str) -> "Graph":
        """Parse an XML string and return a Graph."""
        parser = etree.XMLParser(remove_comments=True, recover=True)
        root: etree._Element = etree.fromstring(
            xml_string.encode() if isinstance(xml_string, str) else xml_string,
            parser,
        )
        tree: etree._ElementTree = root.getroottree()
        return self._parse_tree(tree)

    def _parse_tree(self, tree):
        root_tag = etree.QName(tree.getroot().tag).localname
        self._graph = Graph(graph_id=f"xml_{root_tag}", directed=self.directed)
        self._tree = tree
        self._xpath_to_id = {}
        self._edge_counter = 0
        self._pending_refs = []

        root = tree.getroot()

        # first pass: register all element xpaths so that forward xpath
        # references can be resolved
        self._register_xpaths(root)

        # second pass: build nodes and edges except ref elements
        self._process_element(root, parent_node_id=None, depth=0)

        # third pass: add reference edges
        self._resolve_pending_refs()


        return self._graph

    def _register_xpaths(self, element):
        """Walk the whole tree once and map each element's xpath → a new id."""
        xpath = self._tree.getpath(element)
        node_id = self._make_node_id(element)
        self._xpath_to_id[xpath] = node_id
        for child in element:
            if not isinstance(child.tag, str):
                continue
            self._register_xpaths(child)

    def _make_node_id(self, element: etree._Element) -> str:
        """Generate a short, human-readable but unique node id."""
        tag = etree.QName(element.tag).localname
        xpath = self._tree.getpath(element)
        # strip namespace-qualified brackets from xpath for readability
        short = re.sub(r"\[.*?\]", lambda m: m.group(), xpath)
        return f"{tag}:{short}"

    def _next_edge_id(self) -> str:
        self._edge_counter += 1
        return f"edge_{self._edge_counter}"

    def _process_element(self,element,parent_node_id,depth):
        """
        Pass 2: recursively build nodes and xml_child edges.

        Reference elements (carrying ``reference_attr``) are NOT added as
        nodes here – their source node_id and ref xpath are queued in
        ``_pending_refs`` for Pass 3.
        """
        if not isinstance(element.tag, str):
            return None

        if self.max_depth is not None and depth > self.max_depth:
            return None

        tag = etree.QName(element.tag).localname
        xpath = self._tree.getpath(element)

        # reference element queue for pass 3, do not create a node
        ref_xpath = element.get(self.reference_attr)
        if ref_xpath is not None and parent_node_id is not None:
            self._pending_refs.append((parent_node_id, ref_xpath, tag))
            return None

        # leaf element
        child_elements = [c for c in element if isinstance(c.tag, str)]
        text = (element.text or "").strip()
        if not child_elements and parent_node_id is not None:
            parent_node = self._graph.get_node(parent_node_id)
            if parent_node is not None:
                if text:
                    parent_node.attributes[tag] = _coerce(text)
                else:
                    for attr_name, attr_val in element.attrib.items():
                        if attr_name == self.reference_attr:
                            continue
                        parent_node.attributes[f"{tag}.{attr_name}"] = _coerce(attr_val)
            return None

        # regular element becomes a node
        node_id = self._xpath_to_id[xpath]

        node_attributes: dict[str, Any] = {"_tag": tag}
        if text:
            node_attributes["_text"] = _coerce(text)
        for attr_name, attr_val in element.attrib.items():
            if attr_name == self.reference_attr:
                continue
            node_attributes[attr_name] = _coerce(attr_val)

        node = Node(node_id=node_id, attributes=node_attributes)
        self._graph.add_node(node)

        # Edge from parent to this node
        if parent_node_id is not None:
            edge = Edge(
                edge_id=self._next_edge_id(),
                source=parent_node_id,
                target=node_id,
                attributes={"type": "xml_child", "tag": tag},
            )
            self._graph.add_edge(edge)

        # Recurse into children
        for child in element:
            self._process_element(child, parent_node_id=node_id, depth=depth + 1)

        return node_id

    def _resolve_pending_refs(self):
        """
        Pass 3: resolve all queued reference edges now that every node exists.
        Silently skips references whose target cannot be resolved.
        """
        for source_id, ref_xpath, tag in self._pending_refs:
            target_id = self._resolve_xpath_ref(ref_xpath)
            if target_id is None:
                continue
            # skip if source or target node was not created
            if source_id not in self._graph.nodes:
                continue
            if target_id not in self._graph.nodes:
                continue
            edge = Edge(
                edge_id=self._next_edge_id(),
                source=source_id,
                target=target_id,
                attributes={"type": "xml_reference", "tag": tag},
            )
            self._graph.add_edge(edge)

    def _resolve_xpath_ref(self, ref_xpath):
        """
        Resolve an XPath reference to a node_id.

        Tries absolute lookup first, then evaluates the XPath against the
        document root and maps the resulting element to its registered id.
        """
        # direct xpath-to-id lookup (fast path for absolute paths)
        if ref_xpath in self._xpath_to_id:
            return self._xpath_to_id[ref_xpath]

        # evaluate XPath against the document root
        try:
            results = self._tree.getroot().xpath(ref_xpath)
            if results and isinstance(results[0], etree._Element):
                target_xpath = self._tree.getpath(results[0])
                return self._xpath_to_id.get(target_xpath)
        except etree.XPathError:
            pass

        return None