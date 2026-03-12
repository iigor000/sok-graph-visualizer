"""
Views for SOK Graph Visualizer - Sites App
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

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


def index(request):
    """Main view with panel layout"""
    # Get active workspace from session (default to 1)
    active_workspace_id = request.session.get('active_workspace_id', 1)
    
    # Get workspaces
    workspaces = [
        {'id': 1, 'name': 'Workspace 1', 'active': active_workspace_id == 1},
        {'id': 2, 'name': 'Workspace 2', 'active': active_workspace_id == 2},
        {'id': 3, 'name': 'Workspace 3', 'active': active_workspace_id == 3},
    ]
    
    context = {
        'title': 'SOK Graph Visualizer',
        'workspaces': workspaces,
    }
    
    return render(request, 'index.html', context)


def load_workspace(request, workspace_id):
    """Load workspace by ID (redirects to index)"""
    request.session['active_workspace_id'] = workspace_id
    return redirect('index')


@csrf_exempt
@require_http_methods(["POST"])
def activate_workspace(request, workspace_id):
    """Activate workspace without page reload (AJAX endpoint)"""
    request.session['active_workspace_id'] = workspace_id
    return JsonResponse({
        'success': True,
        'workspace_id': workspace_id,
        'message': f'Workspace {workspace_id} activated'
    })


def render_graph_view(request):
    """Render the graph"""
    if not services_loaded:
        return JsonResponse({
            'error': 'Core services not loaded',
            'success': False
        }, status=500)
    
    try:
        html = render_service.render_active_workspace()
        return JsonResponse({'html': html, 'success': True})
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)


@require_http_methods(["GET"])
def list_workspaces(request):
    """List all workspaces - API endpoint"""
    try:
        workspaces = [
            {'id': 1, 'name': 'Workspace 1', 'active': True},
            {'id': 2, 'name': 'Workspace 2', 'active': False},
            {'id': 3, 'name': 'Workspace 3', 'active': False},
        ]
        return JsonResponse(workspaces, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_workspace(request, workspace_id):
    """Get workspace data by ID - API endpoint"""
    try:
        return JsonResponse({
            'id': workspace_id,
            'name': f'Workspace {workspace_id}',
            'nodes': [],
            'edges': []
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def health(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'services_loaded': services_loaded
    })
