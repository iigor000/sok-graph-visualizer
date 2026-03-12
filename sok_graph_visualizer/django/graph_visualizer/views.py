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
    active_workspace_id = request.session.get("active_workspace_id", 1)

    workspaces = [
        {"id": 1, "name": "Workspace 1", "active": active_workspace_id == 1},
        {"id": 2, "name": "Workspace 2", "active": active_workspace_id == 2},
        {"id": 3, "name": "Workspace 3", "active": active_workspace_id == 3},
    ]

    context = {
        "title": "SOK Graph Visualizer",
        "workspaces": workspaces,
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
        active_workspace_id = request.session.get("active_workspace_id", 1)

        workspaces = [
            {"id": 1, "name": "Workspace 1", "active": active_workspace_id == 1},
            {"id": 2, "name": "Workspace 2", "active": active_workspace_id == 2},
            {"id": 3, "name": "Workspace 3", "active": active_workspace_id == 3},
        ]

        return JsonResponse(workspaces, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def get_workspace(request, workspace_id):
    """
    Get workspace data by ID - API endpoint.
    """
    try:
        active_workspace_id = request.session.get("active_workspace_id", 1)

        return JsonResponse(
            {
                "id": workspace_id,
                "name": f"Workspace {workspace_id}",
                "active": active_workspace_id == workspace_id,
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