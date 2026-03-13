"""
Flask application for SOK Graph Visualizer
"""
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from pathlib import Path
import sys
import json
from jinja2 import nodes
from jinja2.ext import Extension

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from sok_graph_visualizer.api.model.Graph import Graph
    from sok_graph_visualizer.core.src.app import App

    core_app = App()

    services_loaded = True
except Exception as e:
    import traceback
    print(f"Warning: Could not load core services: {e}")
    traceback.print_exc()
    core_app = None
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
    active_workspace = core_app.get_active_workspace() if core_app else None
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
        core_app.execute_command('select_workspace', {'workspace_id': str(session_workspace_id)})

    workspaces = [_serialize_workspace(ws) for ws in core_app.list_workspaces()]
    return render_template('index.html', title='SOK Graph Visualizer', workspaces=workspaces, services_loaded=True)


@app.route('/workspaces')
def workspace_page():
    """Backward-compatible route that now points to the index view."""
    return redirect(url_for('index'))


@app.route('/workspace/<workspace_id>')
def load_workspace(workspace_id: str):
    """Load workspace by ID (redirects to index)"""
    if services_loaded:
        success, message = core_app.execute_command('select_workspace', {'workspace_id': str(workspace_id)})
        if success:
            session['active_workspace_id'] = str(workspace_id)
    return redirect(url_for('workspace_page'))


@app.route('/api/workspace/<workspace_id>/activate', methods=['POST'])
def activate_workspace(workspace_id: str):
    """Activate workspace without page reload (AJAX endpoint)"""
    if not services_loaded:
        return jsonify({'success': False, 'error': 'Core services not loaded'}), 500

    success, message = core_app.execute_command('select_workspace', {'workspace_id': str(workspace_id)})
    if not success:
        return jsonify({'success': False, 'error': f'Workspace not found: {workspace_id}'}), 404

    session['active_workspace_id'] = str(workspace_id)
    workspace = core_app.get_active_workspace()
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
        workspace = core_app.get_active_workspace()
        if workspace is None:
            return jsonify({'error': 'No active workspace', 'success': False}), 400
        
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
        workspaces = [_serialize_workspace(ws) for ws in core_app.list_workspaces()]
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
        success, message = core_app.execute_command('create_workspace', {
            'name': name,
            'data_source_id': data_source_id,
            'config': config
        })
        
        if not success:
            return jsonify({'success': False, 'error': message}), 400

        workspace = core_app.get_active_workspace()
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
        for plugin_id, plugin_class in core_app.plugin_manager.get_data_source_plugins().items():
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
        workspace = core_app.get_workspace(str(workspace_id))
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


@app.route('/api/workspace/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """Delete a workspace by ID"""
    if not services_loaded:
        return jsonify({'success': False, 'error': 'Core services not loaded'}), 500

    try:
        success, message = core_app.execute_command('delete_workspace', {
            'workspace_id': str(workspace_id)
        })
        
        if not success:
            return jsonify({'success': False, 'error': message}), 400

        # Clear session if deleted workspace was active
        if session.get('active_workspace_id') == str(workspace_id):
            session.pop('active_workspace_id', None)

        return jsonify({
            'success': True,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to delete workspace: {str(e)}'}), 400


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'services_loaded': services_loaded
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
