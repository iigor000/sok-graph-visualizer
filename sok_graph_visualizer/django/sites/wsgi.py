"""
WSGI config for SOK Graph Visualizer Django application.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sites.settings')

application = get_wsgi_application()
