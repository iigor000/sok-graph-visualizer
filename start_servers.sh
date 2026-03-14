#!/bin/bash

# SOK Graph Visualizer - Start Both Django and Flask Servers
# This script starts both the Django and Flask development servers in separate terminals

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/test-virt"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}SOK Graph Visualizer - Server Startup${NC}"
echo -e "${BLUE}================================${NC}"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found at $VENV_PATH${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$VENV_PATH/bin/activate"

# Navigate to project root
cd "$PROJECT_ROOT"

# Create a function to run commands in new terminal
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
        echo -e "${YELLOW}⚠ No terminal emulator found, running in background${NC}"
        eval "$COMMAND" > "/tmp/${TITLE}.log" 2>&1 &
    fi
}

# Install dependencies if needed
echo -e "${BLUE}Checking dependencies...${NC}"
pip install -q django flask jinja2 2>/dev/null || true

# Start Django server
echo ""
run_server "Django Server" "python sok_graph_visualizer/django/manage.py runserver 0.0.0.0:8000" "8000"

# Wait a moment for Django to start
sleep 2

# Start Flask server
echo ""
run_server "Flask Server" "python -m sok_graph_visualizer.flask.run" "5000"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ Servers started!${NC}"
echo -e "${GREEN}================================${NC}"
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
