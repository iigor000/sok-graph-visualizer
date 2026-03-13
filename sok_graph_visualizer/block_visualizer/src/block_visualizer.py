from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import os
import json
from datetime import date, datetime
from dataclasses import dataclass
from typing import Dict

# Import API models and service interfaces
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


@dataclass
class VisualNode:
	"""Simple representation of a node for templates"""
	node_id: str
	name: str
	attributes: Dict


@dataclass
class VisualEdge:
	"""Simple representation of an edge for templates"""
	edge_id: str
	source: str
	target: str
	attributes: Dict


class DateTimeEncoder(json.JSONEncoder):
	"""Custom JSON encoder that handles date and datetime objects"""
	def default(self, obj):
		if isinstance(obj, (date, datetime)):
			return obj.isoformat()
		return super().default(obj)


def tojson_with_dates(obj):
	"""Jinja2 filter for JSON serialization that handles dates"""
	json_str = json.dumps(obj, cls=DateTimeEncoder)
	# Return as Markup to prevent HTML escaping in templates
	return Markup(json_str)


env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(['html', 'jinja']))
env.filters['tojson'] = tojson_with_dates

class BlockVisualizer(VisualizerPlugin):
	def get_name(self) -> str:
		return 'Block Visualizer'

	def get_description(self) -> str:
		return 'Renders the graph as a JavaScript visualization fragment.'

	def get_required_scripts(self) -> list[str]:
		return ['https://d3js.org/d3.v7.min.js']

	def render(self, graph: Graph) -> str:
		"""
		Return only the JavaScript fragment (no surrounding HTML). The test runner
		or host app is responsible for providing the full HTML shell (head, styles,
		and the D3 <script> include).
		"""
		if graph.directed:
			tpl = env.get_template('block_directed.jinja')
		else:
			tpl = env.get_template('block.jinja')
		
		# Transform graph data into simpler objects for template rendering
		prepared_nodes = self._prepare_nodes(graph)
		prepared_edges = self._prepare_edges(graph)
		
		# render and return JS source as a string (no enclosing <script> tags)
		return tpl.render(graph_nodes=prepared_nodes, graph_edges=prepared_edges)
	
	def _prepare_nodes(self, graph: Graph) -> Dict[str, VisualNode]:
		"""Transform Node objects into VisualNode dataclasses for template rendering"""
		result: Dict[str, VisualNode] = {}
		for node_id, node in graph.nodes.items():
			result[node_id] = VisualNode(
				node_id=node.node_id,
				name=node.attributes.get("name", node_id),
				attributes=node.attributes,
			)
		return result
	
	def _prepare_edges(self, graph: Graph) -> Dict[str, VisualEdge]:
		"""Transform Edge objects into VisualEdge dataclasses for template rendering"""
		result: Dict[str, VisualEdge] = {}
		for edge_id, edge in graph.edges.items():
			result[edge_id] = VisualEdge(
				edge_id=edge.edge_id,
				source=edge.source,
				target=edge.target,
				attributes=edge.attributes,
			)
		return result
