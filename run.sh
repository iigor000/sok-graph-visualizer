#!/bin/bash

# SOK Graph Visualizer - Complete Setup and Server Startup
# This script installs all dependencies and starts both Django and Flask servers

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/.venv"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SOK Graph Visualizer - Setup & Run${NC}"
echo -e "${BLUE}========================================${NC}"

# ============================================
# SETUP PHASE
# ============================================
echo ""
echo -e "${BLUE}[SETUP]${NC} Preparing virtual environment..."
echo ""

# Create or activate virtual environment
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found"
    source "$VENV_PATH/bin/activate"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found, creating..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

echo ""
echo -e "${BLUE}[SETUP]${NC} Installing dependencies..."
echo ""

cd "$PROJECT_ROOT"

# Install project requirements
echo "   Installing project requirements..."
pip install -r "sok_graph_visualizer/requirements.txt" --quiet --upgrade

# Install root package
echo "   Installing root package (sok-graph-visualizer)..."
pip install -e . --quiet --upgrade

# Install modules in order of dependency
echo "   Installing API module..."
pip install -e "sok_graph_visualizer/api/" --quiet --upgrade

echo "   Installing Core module..."
pip install -e "sok_graph_visualizer/core/" --quiet --upgrade

echo "   Installing Simple Visualizer..."
pip install -e "sok_graph_visualizer/simple_visualizer/" --quiet --upgrade

echo "   Installing Block Visualizer..."
pip install -e "sok_graph_visualizer/block_visualizer/" --quiet --upgrade

echo "   Installing RDF Datasource..."
pip install -e "sok_graph_visualizer/rdf_datasource/" --quiet --upgrade

echo "   Installing XML Datasource..."
pip install -e "sok_graph_visualizer/xml_datasource/" --quiet --upgrade

echo "   Installing JSON Datasource..."
pip install -e "sok_graph_visualizer/json_data_source/" --quiet --upgrade

echo "   Installing Django module..."
pip install -e "sok_graph_visualizer/django/" --quiet --upgrade

echo "   Installing Flask module..."
pip install -e "sok_graph_visualizer/flask/" --quiet --upgrade

echo ""
echo -e "${GREEN}✓${NC} All dependencies installed"

# ============================================
# SERVER STARTUP PHASE
# ============================================
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}[STARTUP]${NC} Starting servers..."
echo -e "${BLUE}========================================${NC}"
echo ""

run_server() {
    local TITLE="$1"
    local COMMAND="$2"
    local PORT="$3"
    
    echo -e "${GREEN}✓${NC} Starting: ${TITLE} (Port ${PORT})"
    
    # Create a new terminal and run the command
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$TITLE" -- bash -c "cd '$PROJECT_ROOT' && source '$VENV_PATH/bin/activate' && $COMMAND; bash"
    elif command -v xterm &> /dev/null; then
        xterm -title "$TITLE" -e "cd '$PROJECT_ROOT' && source '$VENV_PATH/bin/activate' && $COMMAND; bash" &
    elif command -v konsole &> /dev/null; then
        konsole --title "$TITLE" -e bash -c "cd '$PROJECT_ROOT' && source '$VENV_PATH/bin/activate' && $COMMAND; bash" &
    elif [[ "$OSTYPE" == darwin* ]] && command -v open &> /dev/null; then
        # macOS only
        open -a Terminal <<EOF
cd '$PROJECT_ROOT'
source '$VENV_PATH/bin/activate'
$COMMAND
EOF
    else
        # Fallback: run in background
        echo -e "${YELLOW}⚠${NC} No terminal emulator found, running in background"
        eval "$COMMAND" > "/tmp/${TITLE}.log" 2>&1 &
    fi
}

# Start Django server
run_server "Django Server" "python sok_graph_visualizer/django/manage.py runserver 0.0.0.0:8000" "8000"

# Wait a moment for Django to start
sleep 2

# Start Flask server
run_server "Flask Server" "python sok_graph_visualizer/flask/run.py" "5000"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup complete and servers started!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Django  (Core UI):  ${BLUE}http://localhost:8000${NC}"
echo -e "Flask   (API):      ${BLUE}http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Controls:${NC}"
echo -e "  • Scroll wheel in Main View: Zoom in/out"
echo -e "  • Shift+Drag in Main View: Pan"
echo -e "  • Drag red rectangle in Bird View: Pan main view"
echo ""
echo -e "${YELLOW}Press CTRL+C in each terminal to stop${NC}"
echo ""
