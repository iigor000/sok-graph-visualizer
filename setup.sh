#!/bin/bash

# SOK Graph Visualizer - Setup and Install Script
# This script installs all modules in development mode

set -e  # Exit on any error

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "SOK Graph Visualizer - Setup"
echo "=========================================="

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✓ Virtual environment activated"
else
    echo "⚠ Warning: Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "  Creating virtual environment..."
    python -m venv "$PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
    echo "✓ Virtual environment created and activated"
fi

echo ""
echo "Installing dependencies..."
cd "$PROJECT_ROOT"

# Install project requirements first
echo "0. Installing project requirements..."
pip install -r "sok_graph_visualizer/requirements.txt" --quiet --upgrade
echo "   ✓ Project requirements installed"

# Install root package first to make sok_graph_visualizer importable
echo "1. Installing root package..."
pip install -e . --quiet --upgrade
echo "   ✓ sok-graph-visualizer installed"

# Install base dependencies first
echo "2. Installing API module..."
pip install -e "sok_graph_visualizer/api/" --quiet --upgrade
echo "   ✓ graph-api installed"

echo "3. Installing Core module..."
pip install -e "sok_graph_visualizer/core/" --quiet --upgrade
echo "   ✓ graph-platform installed"

echo "4. Installing Simple Visualizer..."
pip install -e "sok_graph_visualizer/simple_visualizer/" --quiet --upgrade
echo "   ✓ graph-simple-visualizer installed"

echo "5. Installing Block Visualizer..."
pip install -e "sok_graph_visualizer/block_visualizer/" --quiet --upgrade
echo "   ✓ graph-block-visualizer installed"

echo "6. Installing RDF Datasource..."
pip install -e "sok_graph_visualizer/rdf_datasource/" --quiet --upgrade
echo "   ✓ graph-rdf-datasource installed"

echo "7. Installing XML Datasource..."
pip install -e "sok_graph_visualizer/xml_datasource/" --quiet --upgrade
echo "   ✓ graph-xml-datasource installed"

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""

