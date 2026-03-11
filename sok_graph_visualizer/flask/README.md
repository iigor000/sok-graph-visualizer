# SOK Graph Visualizer - Flask Application

Flask web application for SOK Graph Visualizer.

## Installation

```bash
cd sok_graph_visualizer/flask
pip install -r requirements.txt
```

## Running the Application

### Development Mode

```bash
python run.py
```

Or using Flask CLI:

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```

### Windows PowerShell

```powershell
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"
python -m flask run
```

The application will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Main application view
- `GET /api/workspaces` - List all workspaces
- `GET /api/workspace/<id>` - Get workspace by ID
- `POST /api/workspace/<id>/render` - Render workspace graph
- `GET /health` - Health check

## Configuration

Configuration is managed in `config.py`. Environment-specific settings can be changed via environment variables:

- `SECRET_KEY` - Secret key for session management
- `FLASK_ENV` - Environment (development/production/testing)
- `FLASK_DEBUG` - Enable debug mode (True/False)

## Project Structure

```
flask/
├── app.py                   # Main Flask application
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Shared Resources

Templates and static files are shared from `core/src/web/`:
- Templates: `../../core/src/web/templates/`
- Static files: `../../core/src/web/static/`
