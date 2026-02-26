"""Test runner for the block visualizer.

Usage (from repository root):

    python -m sok_graph_visualizer.test.run_block_visualizer

This will:
- Build sample graph data using API model classes
- Start a WSGI server that uses `BlockVisualizer` to render HTML

Note: `sok_graph_visualizer.block_visualizer.block_visualizer` is a pure renderer module
and does NOT expose a WSGI `app`. This runner constructs the WSGI app here and
wraps the renderer output into a full HTML document for testing.
"""
import sys
import os
from wsgiref.simple_server import make_server

# Ensure repository root is on sys.path (safe when running as a module)
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Build sample data using the API model classes
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.model.Node import Node as ApiNode
from sok_graph_visualizer.api.model.Edge import Edge as ApiEdge

# Import the BlockVisualizer renderer (the visualizer is responsible only for rendering)
from sok_graph_visualizer.block_visualizer.src.block_visualizer import BlockVisualizer


def build_sample_graph() -> Graph:
    g = Graph('sample', name='Sample Graph', directed=True)

    for i in range(1, 11):
        nid = f'n{i}'
        attrs = {'name': f'Node {i}', 'value': i}
        g.add_node(ApiNode(nid, attrs))

    eid = 1
    for i in range(1, 10):
        g.add_edge(ApiEdge(f'e{eid}', f'n{i}', f'n{i+1}'))
        eid += 1

    # add a couple extra edges
    g.add_edge(ApiEdge(f'e{eid}', 'n1', 'n5'))
    eid += 1
    g.add_edge(ApiEdge(f'e{eid}', 'n2', 'n7'))

    return g


# Build shared samples/renderers used by the WSGI app
SAMPLE_GRAPH = build_sample_graph()
VIS = BlockVisualizer()


def build_full_html(script_fragment: str) -> str:
    """Assemble a minimal full HTML page for testing that includes D3, styles, and the script fragment.

    The visualizer returns only the JavaScript fragment; this function wraps it in a complete HTML document.
    """
    head = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>
    html, body { height: 100%; margin: 0; }
    #main { width: 100%; height: 100vh; background: #ffffff; }
    .node-rect { rx: 6; ry: 6; }
    text { font-family: Arial, Helvetica, sans-serif; }
  </style>
</head>
<body>
  <div id="main"></div>
'''

    tail = '\n</body>\n</html>'

    # embed script inside a single script tag
    full = head + "\n<script>\n" + script_fragment + "\n</script>" + tail
    return full


def app(environ, start_response):
    """WSGI app that returns rendered HTML for the sample graph.

    Routes:
    - / or /index -> undirected view
    - /directed -> directed view
    """
    path = environ.get('PATH_INFO', '/') or '/'
    if path in ('/', '/index'):
        SAMPLE_GRAPH.directed = False
        script = VIS.render(SAMPLE_GRAPH)
        body = build_full_html(script)
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return [body.encode('utf-8')]
    elif path == '/directed':
        SAMPLE_GRAPH.directed = True
        script = VIS.render(SAMPLE_GRAPH)
        body = build_full_html(script)
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return [body.encode('utf-8')]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain; charset=utf-8')])
        return [b'Not Found']


def main(port: int = 8000):
    # Sanity check: render once and print length
    script = VIS.render(SAMPLE_GRAPH)
    full = build_full_html(script)
    print(f"Rendered sample HTML length: {len(full)} characters")

    print(f"Serving block visualizer on http://0.0.0.0:{port} (CTRL+C to stop)")
    with make_server('0.0.0.0', port, app) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped')


if __name__ == '__main__':
    main()

