"""
URL configuration for Graph Explorer app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.index, name='index'),
    path('workspace/<int:workspace_id>/', views.load_workspace, name='load_workspace'),
    path('render/', views.render_graph_view, name='render_graph'),

    # API endpoints
    path('api/workspaces/', views.list_workspaces, name='api_list_workspaces'),
    path('api/workspace/<int:workspace_id>/', views.get_workspace, name='api_get_workspace'),
    path('api/workspace/<int:workspace_id>/activate', views.activate_workspace, name='api_activate_workspace'),
    path('api/plugins/data-sources/', views.list_data_source_plugins, name='api_list_data_source_plugins'),

    # Health check
    path('health/', views.health, name='health'),
]
