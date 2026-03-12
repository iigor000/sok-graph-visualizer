from typing import Any, Callable, Dict, List, Optional
import inspect

from sok_graph_visualizer.core.src.workspace.workspace import Workspace
from sok_graph_visualizer.core.src.workspace.workspace_manager import WorkspaceManager
from sok_graph_visualizer.api.model.Graph import Graph
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin


class RenderService:
    """
    Manages rendering of Graph models.
    
    Contract:
    - VisualizerPlugin.render() receives a Graph object (not dict)
    - VisualizerPlugin.render() must output HTML with 'data-node-id' on node elements
    - Provides event hooks: pre_render, post_render
    """

    def __init__(self, workspace_manager: WorkspaceManager, visualizer: Optional[VisualizerPlugin] = None):
        self.workspace_manager = workspace_manager
        self.visualizer: Optional[VisualizerPlugin] = visualizer
        self._hooks: Dict[str, List[Callable[..., Any]]] = {}

    def set_visualizer(self, visualizer: VisualizerPlugin):
        self.visualizer = visualizer

    def register_hook(self, event: str, fn: Callable[..., Any]):
        self._hooks.setdefault(event, []).append(fn)

    def _emit(self, event: str, **kwargs):
        for fn in self._hooks.get(event, []):
            fn(**kwargs)

    def render_active_workspace(self) -> str:
        """
        Render the active workspace's graph using the visualizer plugin.
        
        Returns:
            HTML string from the visualizer (must include data-node-id on nodes)
        """
        if self.workspace_manager.active_workspace_id is None:
            raise RuntimeError("No active workspace")
        
        workspace: Workspace = self.workspace_manager.workspaces.get(self.workspace_manager.active_workspace_id)
        if workspace is None:
            raise RuntimeError("Active workspace not found")
        visualizer = workspace.visualizer_plugin or self.visualizer
        if visualizer is None:
            raise RuntimeError("No visualizer plugin selected")

        graph: Graph = workspace.current_graph

        # hook before render
        self._emit("pre_render", graph=graph, workspace=workspace)

        # pass Graph model directly; visualizer is responsible for data-node-id in HTML
        result = visualizer.render(graph)

        # hook after render
        self._emit("post_render", graph=graph, workspace=workspace, result=result)

        return result

    @staticmethod
    def is_concrete_visualizer(obj: Any) -> bool:
        """True if obj is an instance of VisualizerPlugin and not abstract."""
        if not isinstance(obj, VisualizerPlugin):
            return False
        return not inspect.isabstract(obj.__class__)