"""
Views for Graph Visualizer
"""
from django.apps import apps
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def _get_app_config():
    """
    Return the Django app configuration for graph_visualizer.
    """
    return apps.get_app_config("graph_visualizer")


def index(request):
    """
    Main view with panel layout.
    """
    context = {
        "title": "SOK Graph Visualizer",
    }

    return render(request, "index.html", context)


def load_workspace(request, workspace_id):
    """
    Load workspace by ID and redirect to index page.
    """
    request.session["active_workspace_id"] = workspace_id
    return redirect("index")


@csrf_exempt
@require_http_methods(["POST"])
def activate_workspace(request, workspace_id):
    """
    Activate workspace without page reload (AJAX endpoint).
    """
    request.session["active_workspace_id"] = workspace_id

    return JsonResponse(
        {
            "success": True,
            "workspace_id": workspace_id,
            "message": f"Workspace {workspace_id} activated",
        }
    )


def render_graph_view(request):
    """
    Render the graph of the active workspace.
    """
    config = _get_app_config()
    render_service = config.render_service

    try:
        html = render_service.render_active_workspace()
        return JsonResponse({"html": html, "success": True})
    except Exception as e:
        return JsonResponse(
            {
                "error": str(e),
                "success": False,
            },
            status=500,
        )


@require_http_methods(["GET"])
def list_workspaces(request):
    """
    List all workspaces - API endpoint.
    """
    try:
        # Return empty list - workspaces will be created via user interaction
        workspaces = []
        return JsonResponse(workspaces, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_workspace(request, workspace_id):
    """
    Get workspace data by ID - API endpoint.
    """
    try:
        # Return minimal workspace data
        return JsonResponse(
            {
                "id": workspace_id,
                "name": f"Workspace {workspace_id}",
                "active": False,
                "nodes": [],
                "edges": [],
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def health(request):
    """
    Health check endpoint.
    """
    try:
        _get_app_config()
        services_loaded = True
    except Exception:
        services_loaded = False

    return JsonResponse(
        {
            "status": "ok",
            "services_loaded": services_loaded,
        }
    )


@csrf_exempt
@require_http_methods(["GET"])
def list_data_source_plugins(request):
    """
    List available data source plugins and their required config fields.
    """
    try:
        config = _get_app_config()
        plugin_manager = config.plugin_manager
        
        if not plugin_manager or not plugin_manager._data_sources:
            return JsonResponse({'error': 'Data source plugins not available'}, status=500)

        plugins = []
        
        for plugin_id, plugin_class in plugin_manager._data_sources.items():
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
        return JsonResponse({'plugins': plugins})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)