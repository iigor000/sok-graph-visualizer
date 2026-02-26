from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

# Import API models and service interfaces
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape(['html', 'jinja']))

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
		# render and return JS source as a string (no enclosing <script> tags)
		return tpl.render(graph_nodes=graph.nodes, graph_edges=graph.edges)
