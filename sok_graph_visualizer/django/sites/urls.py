"""
URL configuration for SOK Graph Visualizer Django application
"""
from django.contrib import admin
from django.urls import path, include
from sites import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Main views
    path('', views.index, name='index'),
    path('workspace/<int:workspace_id>/', views.load_workspace, name='load_workspace'),
    path('render/', views.render_graph_view, name='render_graph'),
    
    # API endpoints
    path('api/workspaces/', views.list_workspaces, name='api_list_workspaces'),
    path('api/workspace/<int:workspace_id>/', views.get_workspace, name='api_get_workspace'),
    path('api/workspace/<int:workspace_id>/activate', views.activate_workspace, name='api_activate_workspace'),
    
    # App-specific routes
    path('webshop/', include('webshop.urls')),
    
    # Health check
    path('health/', views.health, name='health'),
]
