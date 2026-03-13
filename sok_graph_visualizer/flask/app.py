"""
Flask application for SOK Graph Visualizer
"""
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from pathlib import Path
import sys
from jinja2 import nodes
from jinja2.ext import Extension

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from sok_graph_visualizer.api.model.Graph import Graph
    from sok_graph_visualizer.core.src.app import App

    # Initialize core application
    core_app = App()
    workspace_manager = core_app.workspace_manager
    plugin_manager = core_app.plugin_manager

    services_loaded = True
except Exception as e:
    import traceback
    print(f"Warning: Could not load core services: {e}")
    traceback.print_exc()
    core_app = None
    workspace_manager = None
    plugin_manager = None
    services_loaded = False


# Jinja2 extension to ignore Django {% load %} tags
class IgnoreLoadExtension(Extension):
    """Extension to ignore Django {% load %} tags in Flask/Jinja2"""
    tags = {'load'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Skip everything until block_end
        while parser.stream.current.type != 'block_end':
            next(parser.stream)
        # Return empty output
        return nodes.Output([nodes.TemplateData('')], lineno=lineno)


# Flask app configuration
app = Flask(
    __name__,
    template_folder=str(Path(__file__).resolve().parent.parent / 'core' / 'src' / 'web' / 'templates'),
    static_folder=str(Path(__file__).resolve().parent.parent / 'core' / 'src' / 'web' / 'static'),
    static_url_path='/static'
)
app.url_map.strict_slashes = False 

# Add Jinja2 extension to ignore {% load %} tags
app.jinja_env.add_extension(IgnoreLoadExtension)

app.config['APP_NAME'] = 'sok-graph-visualizer'
app.secret_key = 'super_secret_random_string_for_session_change_in_production'

# Add 'static' filter for Django-style template syntax
@app.template_filter('static')
def static_filter(path):
    """Template filter to generate static file URLs"""
    return url_for('static', filename=path)


def _serialize_workspace(workspace):
    active_workspace = workspace_manager.get_active_workspace() if workspace_manager else None
    return {
        'id': workspace.workspace_id,
        'name': workspace.name,
        'active': active_workspace is not None and active_workspace.workspace_id == workspace.workspace_id
    }


@app.route('/')
def index():
    """Main view with panel layout."""
    if not services_loaded:
        return render_template('index.html', title='SOK Graph Visualizer', workspaces=[], services_loaded=False)

    session_workspace_id = session.get('active_workspace_id')
    if session_workspace_id:
        workspace_manager.set_active_workspace(str(session_workspace_id))

    workspaces = [_serialize_workspace(ws) for ws in workspace_manager.list_workspaces()]
    return render_template('index.html', title='SOK Graph Visualizer', workspaces=workspaces, services_loaded=True)


@app.route('/workspaces')
def workspace_page():
    """Backward-compatible route that now points to the index view."""
    return redirect(url_for('index'))


@app.route('/workspace/<workspace_id>')
def load_workspace(workspace_id: str):
    """Load workspace by ID (redirects to index)"""
    if services_loaded and workspace_manager.set_active_workspace(str(workspace_id)):
        session['active_workspace_id'] = str(workspace_id)
    return redirect(url_for('workspace_page'))


@app.route('/api/workspace/<workspace_id>/activate', methods=['POST'])
def activate_workspace(workspace_id: str):
    """Activate workspace without page reload (AJAX endpoint)"""
    if not services_loaded:
        return jsonify({'success': False, 'error': 'Core services not loaded'}), 500

    if not workspace_manager.set_active_workspace(str(workspace_id)):
        return jsonify({'success': False, 'error': f'Workspace not found: {workspace_id}'}), 404

    session['active_workspace_id'] = str(workspace_id)
    workspace = workspace_manager.get_active_workspace()
    return jsonify({
        'success': True,
        'workspace': _serialize_workspace(workspace),
        'message': f'Workspace {workspace.name} activated'
    })


@app.route('/render')
def render_graph():
    """Render the graph"""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded', 'success': False}), 500
    
    try:
        # Get active workspace
        if workspace_manager.active_workspace_id is None:
            return jsonify({'error': 'No active workspace', 'success': False}), 400
        
        workspace = workspace_manager.workspaces.get(workspace_manager.active_workspace_id)
        if workspace is None:
            return jsonify({'error': 'Active workspace not found', 'success': False}), 400
        
        # Get visualizer plugin from workspace
        visualizer = workspace.visualizer_plugin
        if visualizer is None:
            return jsonify({'error': 'No visualizer plugin selected', 'success': False}), 400
        
        # Render using the visualizer plugin directly
        html = visualizer.render(workspace.current_graph)
        return jsonify({'html': html, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# API Endpoints

@app.route('/api/workspaces', methods=['GET'])
def list_workspaces():
    """List all workspaces"""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded'}), 500

    try:
        workspaces = [_serialize_workspace(ws) for ws in workspace_manager.list_workspaces()]
        return jsonify(workspaces)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workspaces', methods=['POST'])
def create_workspace():
    """Create a workspace using selected data source plugin and configuration."""
    if not services_loaded:
        return jsonify({'success': False, 'error': 'Core services not loaded'}), 500

    payload = request.get_json(silent=True) or {}
    name = payload.get('name')
    data_source_id = payload.get('data_source_id')
    config = payload.get('config', {})

    if not name:
        return jsonify({'success': False, 'error': "Missing 'name'"}), 400
    if not data_source_id:
        return jsonify({'success': False, 'error': "Missing 'data_source_id'"}), 400

    try:
        data_source_plugin = plugin_manager.instantiate_data_source(data_source_id, config=config)
        graph = data_source_plugin.parse()
        workspace = workspace_manager.create_workspace(
            base_graph=graph,
            name=name,
            data_source_plugin=data_source_plugin,
            set_active=True
        )
        session['active_workspace_id'] = workspace.workspace_id

        return jsonify({
            'success': True,
            'workspace': _serialize_workspace(workspace),
            'message': f'Created workspace {workspace.name}'
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to create workspace: {str(e)}'}), 400


@app.route('/api/plugins/data-sources', methods=['GET'])
def list_data_source_plugins():
    """List available data source plugins and their required config fields."""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded'}), 500

    try:
        plugins = []
        for plugin_id, plugin_class in plugin_manager.get_data_source_plugins().items():
            plugin_instance = plugin_class(config={})
            required_config = plugin_instance.get_required_config()
            plugins.append({
                'id': plugin_id,
                'name': plugin_instance.get_name(),
                'required_config': [
                    {'key': key, 'description': description}
                    for key, description in required_config.items()
                ]
            })
        return jsonify({'plugins': plugins})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workspace/<workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """Get workspace data by ID"""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded'}), 500

    try:
        workspace = workspace_manager.get_workspace(str(workspace_id))
        if workspace is None:
            return jsonify({'error': f'Workspace not found: {workspace_id}'}), 404

        return jsonify({
            'id': workspace.workspace_id,
            'name': workspace.name,
            'nodes': list(workspace.current_graph.nodes.keys()),
            'edges': list(workspace.current_graph.edges.keys())
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'services_loaded': services_loaded
    })

@app.route('/api/workspace/graph', methods=['GET'])
def get_graph_data():
    """Return active workspace graph as JSON for Tree View."""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded'}), 500

    try:
        workspace = workspace_manager.get_active_workspace()
        if workspace is None or workspace.current_graph is None:
            return jsonify({'error': 'No graph loaded'}), 404

        graph = workspace.current_graph

        nodes = [
            {'id': nid, 'attributes': node.attributes or {}}
            for nid, node in graph.nodes.items()
        ]
        edges = [
            {'id': eid, 'source': edge.source, 'target': edge.target, 'attributes': edge.attributes or {}}
            for eid, edge in graph.edges.items()
        ]

        return jsonify({'nodes': nodes, 'edges': edges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plugins/visualizers', methods=['GET'])
def list_visualizer_plugins():
    """List available visualizer plugins."""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded'}), 500

    try:
        plugins = [
            {'id': pid, 'name': pid.replace('_', ' ').title()}
            for pid in plugin_manager.get_visualizer_plugins().keys()
        ]
        return jsonify({'plugins': plugins})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workspace/visualizer/', methods=['POST'])
def set_visualizer():
    """Set visualizer for active workspace and render graph."""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded'}), 500

    payload = request.get_json(silent=True) or {}
    visualizer_id = payload.get('visualizer_id')

    if not visualizer_id:
        return jsonify({'error': 'No visualizer_id specified'}), 400

    try:
        workspace = workspace_manager.get_active_workspace()
        if workspace is None:
            return jsonify({'error': 'No active workspace', 'success': False}), 400

        visualizer = plugin_manager.instantiate_visualizer(visualizer_id)
        workspace.visualizer_plugin = visualizer

        html = visualizer.render(workspace.current_graph)

        if '<script>' in html:
            wrapped = f'<div id="main" style="width:100%;height:100%;position:relative;"></div>{html}'
        else:
            wrapped = f'<div id="main" style="width:100%;height:100%;position:relative;"></div><script>{html}</script>'

        return jsonify({'success': True, 'html': wrapped, 'message': 'Visualizer set'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
