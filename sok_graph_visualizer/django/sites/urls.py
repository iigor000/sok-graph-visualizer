"""
Root URL configuration for Graph Visualizer Django project
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Graph Explorer app routes
    path('', include('graph_visualizer.urls')),
]