# SOK Graph Visualizer - Django Application

Django web application for SOK Graph Visualizer.

## Structure

```
django/
├── sites/           # Django project configuration + main views
│   ├── settings.py  # Django project settings
│   ├── urls.py      # Main URL routing
│   ├── wsgi.py      # WSGI entry point
│   ├── asgi.py      # ASGI entry point
│   └── views.py     # Main views (workspace, render, API)
├── webshop/         # Webshop Django app
│   ├── apps.py      # App configuration
│   ├── views.py     # Webshop views
│   ├── models.py    # Webshop models
│   ├── urls.py      # Webshop URL routing
│   ├── tests.py     # Unit tests
│   ├── admin.py     # Admin configuration
│   └── templatetags/ # Template filters (shared by all templates)
│       └── shared_filters.py  # Shared template filters for Django-Flask compatibility
└── manage.py        # Django management script
```

### Sites Folder

**Dual Purpose:**
1. **Django project configuration** - Central settings, routing, and deployment
2. **Main application logic** - Core views and functionality

**Files:**
- `settings.py` - Django project settings (database, middleware, apps, templates, static)
- `urls.py` - Main URL routing configuration
- `wsgi.py` - WSGI application entry point for deployment
- `asgi.py` - ASGI application entry point for async deployment
- `views.py` - Main view functions (workspace management, graph rendering, API endpoints)

**Note**: `sites/` is NOT a Django app - it's the project configuration folder. Only `webshop/` is registered in INSTALLED_APPS.

### Webshop Folder

Standard Django app prepared for future e-commerce features. Currently hosts the custom template tags used by the main application (Django requires template tags to be in registered apps).

**Template Tags:**
- `templatetags/shared_filters.py` - Shared template filters for Django-Flask compatibility

**Usage in templates:**
```django
{% load shared_filters %}
<link rel="stylesheet" href="{{ 'css/style.css'|static }}">
```

## Installation

```bash
cd sok_graph_visualizer/django
pip install -r requirements.txt
```

## Running the Application

### Development Mode

```bash
python manage.py runserver
```

Or specify host and port:

```bash
python manage.py runserver 0.0.0.0:8000
```

### Windows PowerShell

```powershell
cd sok_graph_visualizer\django
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Initial Setup

Run migrations (first time only):

```bash
python manage.py migrate
```

Create superuser for admin access (optional):

```bash
python manage.py createsuperuser
```


## URL Endpoints

- `/` - Main visualizer interface
- `/workspace/<id>/` - Load workspace by ID  
- `/render/` - Render graph visualization
- `/api/workspaces/` - List all workspaces (API)
- `/api/workspace/<id>/` - Get workspace data (API)
- `/webshop/` - Webshop routes (future)
- `/health/` - Health check
- `/admin/` - Django admin interface

## Configuration

Configuration is managed in `sites/settings.py`. Key settings:

- `SECRET_KEY` - Secret key for cryptographic signing
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - List of allowed host/domain names
- `DATABASES` - Database configuration (default: SQLite)
- `INSTALLED_APPS` - Registered apps: `webshop` (sites is not an app, just configuration)
- `ROOT_URLCONF` - Main URL configuration: `sites.urls`
- `WSGI_APPLICATION` - WSGI application: `sites.wsgi.application`

## Shared Resources

Templates and static files are shared from `core/src/web/`:
- Templates: `../../core/src/web/templates/`
- Static files: `../../core/src/web/static/`

**Template Tags**: Located here because Django requires template tag libraries to be inside registered apps. The `shared_filters` library contains filters used by shared templates for Django-Flask compatibility.

## Shared Resources

Templates and static files are shared from `core/src/web/`:
- Templates: `../../core/src/web/templates/`
- Static files: `../../core/src/web/static/`

## Database

By default, Django uses SQLite database (`db.sqlite3`). To reset the database:

```bash
rm db.sqlite3
python manage.py migrate
```

## Collecting Static Files (Production)

```bash
python manage.py collectstatic
```
