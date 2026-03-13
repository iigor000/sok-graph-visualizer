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
    try:
        config = _get_app_config()
        command_processor = config.command_processor
        workspace_manager = config.workspace_manager
        
        # Execute the SELECT_WORKSPACE command to activate in workspace manager
        success, message = command_processor.execute_command('select_workspace', {
            'workspace_id': workspace_id
        })
        
        if not success:
            return JsonResponse(
                {
                    "success": False,
                    "error": message,
                    "message": f"Failed to activate workspace: {message}",
                },
                status=400
            )
        
        request.session["active_workspace_id"] = workspace_id
        
        return JsonResponse(
            {
                "success": True,
                "workspace_id": workspace_id,
                "message": f"Workspace {workspace_id} activated",
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {
                "success": False,
                "error": str(e),
                "message": f"Error activating workspace: {str(e)}",
            },
            status=500
        )


def render_graph_view(request):
    """
    Render the graph of the active workspace.
    """
    config = _get_app_config()
    workspace_manager = config.workspace_manager

    try:
        # Get active workspace
        if workspace_manager.active_workspace_id is None:
            return JsonResponse({"error": "No active workspace", "success": False}, status=400)
        
        workspace = workspace_manager.workspaces.get(workspace_manager.active_workspace_id)
        if workspace is None:
            return JsonResponse({"error": "Active workspace not found", "success": False}, status=400)
        
        # Get visualizer plugin from workspace or use default
        visualizer = workspace.visualizer_plugin
        if visualizer is None:
            return JsonResponse({"error": "No visualizer plugin selected", "success": False}, status=400)
        
        # Render using the visualizer plugin directly
        html = visualizer.render(workspace.current_graph)
        return JsonResponse({"html": html, "success": True})
    except Exception as e:
        return JsonResponse(
            {
                "error": str(e),
                "success": False,
            },
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def list_workspaces(request):
    """
    List all workspaces (GET) or create a new workspace (POST) - API endpoint.
    """
    config = _get_app_config()
    workspace_manager = config.workspace_manager
    command_processor = config.command_processor
    
    if request.method == 'GET':
        try:
            # Return list of all workspaces
            workspaces = []
            for workspace_id, workspace in workspace_manager.workspaces.items():
                workspaces.append({
                    'id': workspace.workspace_id,
                    'name': workspace.name,
                    'active': workspace_manager.active_workspace_id == workspace_id,
                    'nodes': len(workspace.current_graph.nodes) if workspace.current_graph else 0,
                    'edges': len(workspace.current_graph.edges) if workspace.current_graph else 0,
                })
            return JsonResponse(workspaces, safe=False)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            import json
            
            body = json.loads(request.body)
            
            name = body.get('name')
            data_source_id = body.get('data_source_id')
            config = body.get('config', {})
            
            if not name or not data_source_id:
                return JsonResponse({'error': 'Missing required fields: name or data_source_id'}, status=400)
            
            # Execute the CREATE_WORKSPACE command
            success, message = command_processor.execute_command('create_workspace', {
                'name': name,
                'data_source_id': data_source_id,
                'config': config
            })
            
            if not success:
                return JsonResponse({'error': message}, status=400)
            
            # Get the newly created workspace
            workspace_id = workspace_manager.active_workspace_id
            workspace = workspace_manager.workspaces.get(workspace_id)
            
            if workspace is None:
                return JsonResponse({'error': 'Workspace created but not found'}, status=500)
            
            response_data = {
                'id': workspace.workspace_id,
                'name': workspace.name,
                'data_source_id': data_source_id,
                'config': config
            }
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)


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
            try:
                plugin_instance = plugin_class(config={})
                required_config = plugin_instance.get_required_config()
                plugin_data = {
                    'id': plugin_id,
                    'name': plugin_instance.get_name(),
                    'required_config': [
                        {'key': key, 'description': description}
                        for key, description in required_config.items()
                    ]
                }
                plugins.append(plugin_data)
            except Exception as plugin_error:
                raise
        
        response_data = {'plugins': plugins}
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_visualizer_plugins(request):
    """
    List available visualizer plugins.
    """
    try:
        config = _get_app_config()
        
        plugin_manager = config.plugin_manager
        
        if not plugin_manager:
            return JsonResponse({'error': 'Plugin manager not available'}, status=500)
        
        visualizers = plugin_manager._data_visualizers or {}
        if not visualizers:
            return JsonResponse({'plugins': []})

        plugins = []
        
        # Get visualizer names - use simple visualization based on class name
        for plugin_id in visualizers.keys():
            plugin_data = {
                'id': plugin_id,
                'name': plugin_id.replace('_', ' ').title()  # e.g., "simple_visualizer" -> "Simple Visualizer"
            }
            plugins.append(plugin_data)
        
        response_data = {'plugins': plugins}
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def set_visualizer(request):
    """
    Set the visualizer for the active workspace and render the graph.
    """
    try:
        import json
        
        body = json.loads(request.body)
        visualizer_id = body.get('visualizer_id')
        
        print(f'[DEBUG] set_visualizer called with visualizer_id: {visualizer_id}')
        
        if not visualizer_id:
            print('[DEBUG] No visualizer_id specified')
            return JsonResponse({'error': 'No visualizer_id specified'}, status=400)
        
        config = _get_app_config()
        command_processor = config.command_processor
        workspace_manager = config.workspace_manager
        
        # Execute the SELECT_VISUALIZER command
        success, message = command_processor.execute_command('select_visualizer', {
            'visualizer_id': visualizer_id
        })
        
        if not success:
            print(f'[DEBUG] select_visualizer failed: {message}')
            return JsonResponse({'success': False, 'error': message}, status=400)
        
        # Now render the graph with the new visualizer
        if workspace_manager.active_workspace_id is None:
            print('[DEBUG] No active workspace')
            return JsonResponse({'error': 'No active workspace', 'success': False}, status=400)
        
        workspace = workspace_manager.workspaces.get(workspace_manager.active_workspace_id)
        if workspace is None:
            print(f'[DEBUG] Workspace not found: {workspace_manager.active_workspace_id}')
            return JsonResponse({'error': 'Active workspace not found', 'success': False}, status=400)
        
        visualizer = workspace.visualizer_plugin
        if visualizer is None:
            print('[DEBUG] Visualizer not set after select_visualizer command')
            return JsonResponse({'error': 'Visualizer not set', 'success': False}, status=400)
        
        print(f'[DEBUG] Rendering graph with visualizer: {visualizer.get_name()}')
        html = visualizer.render(workspace.current_graph)
        print(f'[DEBUG] Visualizer returned HTML length: {len(html)}')
        print(f'[DEBUG] First 200 chars: {html[:200]}')
        print(f'[DEBUG] Contains <script> tag: {"<script>" in html}')
        
        # Wrap the visualizer script with the main SVG container
        # D3 is already loaded in base.html
        # Check if HTML already has script tags
        if '<script>' in html:
            wrapped_html = f'''
        <div id="main" style="width: 100%; height: 100%; position: relative;"></div>
        {html}
        '''
        else:
            # Wrap javascript code in script tags
            wrapped_html = f'''
        <div id="main" style="width: 100%; height: 100%; position: relative;"></div>
        <script>
{html}
        </script>
        '''
        
        print(f'[DEBUG] Wrapped HTML length: {len(wrapped_html)}')
        print(f'[DEBUG] Wrapped HTML first 300 chars: {wrapped_html[:300]}')
        
        return JsonResponse({
            'success': True,
            'message': message,
            'html': wrapped_html
        })
    except json.JSONDecodeError as e:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
    
@require_http_methods(["GET"])
def get_graph_data(request):
    """
    Return the active workspace's graph as JSON {nodes, edges}
    for the Tree View.
    """
    try:
        config = _get_app_config()
        workspace_manager = config.workspace_manager

        if workspace_manager.active_workspace_id is None:
            return JsonResponse({"error": "No active workspace"}, status=404)

        workspace = workspace_manager.workspaces.get(workspace_manager.active_workspace_id)
        if workspace is None or workspace.current_graph is None:
            return JsonResponse({"error": "No graph loaded"}, status=404)

        graph = workspace.current_graph

        nodes = []
        for node_id, node in graph.nodes.items():
            nodes.append({
                "id": node_id,
                "attributes": node.attributes or {}
            })

        edges = []
        for edge_id, edge in graph.edges.items():
            edges.append({
                "id": edge_id,
                "source": edge.source,
                "target": edge.target,
                "attributes": edge.attributes or {}
            })

        return JsonResponse({"nodes": nodes, "edges": edges})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)