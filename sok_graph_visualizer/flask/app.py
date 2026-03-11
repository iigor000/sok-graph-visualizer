"""
Flask application for SOK Graph Visualizer
"""
from flask import Flask, render_template, session, redirect, url_for, jsonify
from pathlib import Path
import sys
from jinja2 import nodes
from jinja2.ext import Extension

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    from sok_graph_visualizer.core.src.use_cases.render_service import RenderService
    from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager
    
    # Initialize services
    workspace_manager = WorkspaceManager()
    render_service = RenderService(workspace_manager)
    services_loaded = True
except Exception as e:
    print(f"Warning: Could not load core services: {e}")
    workspace_manager = None
    render_service = None
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


@app.route('/')
def index():
    """Main view with panel layout"""
    # Get active workspace from session (default to 1)
    active_workspace_id = session.get('active_workspace_id', 1)
    
    # Get workspaces
    workspaces = [
        {'id': 1, 'name': 'Workspace 1', 'active': active_workspace_id == 1},
        {'id': 2, 'name': 'Workspace 2', 'active': active_workspace_id == 2},
        {'id': 3, 'name': 'Workspace 3', 'active': active_workspace_id == 3},
    ]
    
    return render_template('index.html',
                         title='SOK Graph Visualizer',
                         workspaces=workspaces)


@app.route('/workspace/<int:workspace_id>')
def load_workspace(workspace_id: int):
    """Load workspace by ID (redirects to index)"""
    session['active_workspace_id'] = workspace_id
    return redirect(url_for('index'))


@app.route('/api/workspace/<int:workspace_id>/activate', methods=['POST'])
def activate_workspace(workspace_id: int):
    """Activate workspace without page reload (AJAX endpoint)"""
    session['active_workspace_id'] = workspace_id
    return jsonify({
        'success': True,
        'workspace_id': workspace_id,
        'message': f'Workspace {workspace_id} activated'
    })


@app.route('/render')
def render_graph():
    """Render the graph"""
    if not services_loaded:
        return jsonify({'error': 'Core services not loaded', 'success': False}), 500
    
    try:
        html = render_service.render_active_workspace()
        return jsonify({'html': html, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


# API Endpoints

@app.route('/api/workspaces', methods=['GET'])
def list_workspaces():
    """List all workspaces"""
    try:
        workspaces = [
            {'id': 1, 'name': 'Workspace 1', 'active': True},
            {'id': 2, 'name': 'Workspace 2', 'active': False},
            {'id': 3, 'name': 'Workspace 3', 'active': False},
        ]
        return jsonify(workspaces)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workspace/<int:workspace_id>', methods=['GET'])
def get_workspace(workspace_id):
    """Get workspace data by ID"""
    try:
        return jsonify({
            'id': workspace_id,
            'name': f'Workspace {workspace_id}',
            'nodes': [],
            'edges': []
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
