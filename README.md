# SOK Graph Visualizer

A modular graph visualization platform built with **Django** and **Flask**, utilizing a plugin-based architecture. This tool allows for dynamic graph exploration, manipulation through a built-in CLI, and multiple visualization styles.

## Team
**Team 13**
* **Sara Cvjetković SV78/2023**
* **Andjela Broćeta SV75/2023**
* **Elena Vuković SV77/2023**
* **Mia Uglješić SV22/2023**
* **Igor Novaković SV29/2023**

## Architecture Overview
The project is built using a component-based approach where each module is treated as a separate package installed in "editable" mode. This ensures high modularity and extensibility.

* **`api`**: Defines the core models (`Edge`, `Node`, `Graph`) and the standard interfaces (base classes) that all data source and visualizer plugins must implement.
* **`core`**: Contains the central application logic, including graph processing algorithms, workspace management, and the implementation of CLI commands.
* **`django`**: A robust web platform built with the Django framework, providing a full-featured UI for workspace management and interactive graph exploration.
* **`flask`**: A lightweight, independent web platform built with the Flask framework, offering an alternative environment for viewing and interacting with graphs.
* **`simple_visualizer`**: A visualizer plugin that renders the graph as a minimalist node-link diagram, focusing on high-level connectivity.
* **`block_visualizer`**: A detailed visualizer plugin that displays nodes as data blocks, allowing users to see all internal attributes and properties at a glance.
* **`json_data_source`**: A data source plugin designed to parse and import graph structures from dynamic JSON files.
* **`rdf_datasource`**: A data source plugin that supports the semantic web by importing graphs from Turtle (`.ttl`) and other RDF formats.
* **`xml_datasource`**: A data source plugin that enables loading and transforming structured XML data into the internal graph model.
* **`tests`**: A comprehensive suite of automated tests designed to verify the integrity of the core logic, API compliance, and plugin functionality.

## Installation & Setup

We provide automated bash scripts to handle the installation of multiple components and the virtual environment.

### Prerequisites
* **Python 3.10** or higher
* **Bash shell** (Linux, macOS, or Git Bash on Windows)

### 1. Automated Setup & Run (Recommended)
The fastest way to install all dependencies and start the servers is using the `run.sh` script.

```bash
chmod +x run.sh
./run.sh
```

### 2. Manual Component Installation
If you prefer to install components individually using the provided setup script:

```bash
chmod +x setup.sh
./setup.sh
```

Alternatively, you can install each module manually using the Python module installer. Ensure your virtual environment is active and run:

```bash
# Install core requirements
python -m pip install -r sok_graph_visualizer/requirements.txt

# Install all modules in editable mode
python -m pip install -e .
python -m pip install -e sok_graph_visualizer/api/
python -m pip install -e sok_graph_visualizer/core/
python -m pip install -e sok_graph_visualizer/simple_visualizer/
python -m pip install -e sok_graph_visualizer/block_visualizer/
python -m pip install -e sok_graph_visualizer/rdf_datasource/
python -m pip install -e sok_graph_visualizer/xml_datasource/
python -m pip install -e sok_graph_visualizer/json_data_source/
```

## Web Interface

### **Main View**
Use the **scroll wheel to zoom** and **Shift + Drag to pan** across the graph.

### **Bird's Eye View**
A navigation aid located in the corner of the interface.  
Drag the **red rectangle** to quickly reposition the main viewport.

### **Tree View**
Explore the graph hierarchy in a **nested structure**, similar to a file explorer.

### **Switching Visualizers**
Easily switch between **"Simple"** and **"Block"** views in real-time.


---

## CLI Command Syntax

### Integrated CLI

The platform features an **embedded Command Line Interface (CLI)** for programmatic control.

Below are examples of supported CLI commands.

### **Node Commands**
```bash
create node --id=1 --prop Name=Alice --prop Age=25
edit node --id=1 --prop Age=40
delete node --id=2

create edge --id=1 --source=1 --target=2 --prop Name=Siblings
edit edge --id=1 --prop Name=Friends
delete edge --id=1

filter 'Age>30'
search Tom
clear
```

---

## Data Sources

Configure your workspace to load data from multiple formats using the built-in plugins:

- **RDF**
- **XML**
- **JSON**
