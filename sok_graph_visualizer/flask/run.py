"""
Flask application entry point
"""
import sys
from pathlib import Path

# Add the parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
