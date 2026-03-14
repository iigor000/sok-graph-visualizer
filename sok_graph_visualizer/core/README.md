# Platform Module

This module contains platform-level components for the SOK Graph Visualizer.

## Components

### Workspace Management
Location: [src/workspace/](src/workspace/)

Provides workspace management functionality including:
- **Operation tracking** for graph transformations
- **Workspace state management** (base graph, current graph, history)
- **Undo/redo functionality**
- **Multi-workspace management**
- **Metadata and node selection tracking**

#### Module Structure
```
workspace/
├── __init__.py      # Package exports
├── operation.py     # Operation class
└── workspace.py     # Workspace class
```

#### Quick Start
```python
from use_cases.workspace_service import WorkspaceService
from api.model.Graph import Graph

# Create service
service = WorkspaceService()

# Create workspace
workspace = service.create_workspace(
    base_graph=my_graph,
    name="My Workspace"
)

# Apply operations
workspace.apply_operation(
    new_graph=modified_graph,
    operation_type="transform",
    plugin_name="MyPlugin"
)

# Undo/Redo
service.undo()
service.redo()
```

See inline documentation in [operation.py](src/workspace/operation.py), [workspace.py](src/workspace/workspace.py), and [workspace_service.py](src/use_cases/workspace_service.py) for detailed API reference.

## Testing

Tests are located in the [test/workspace/](../../test/workspace/) directory.

Run all workspace tests:
```bash
python test/workspace/test_workspace.py
```
