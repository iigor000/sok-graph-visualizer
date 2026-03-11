from importlib.metadata import entry_points
import logging
from sok_graph_visualizer.api.service.DataVisualizerService import VisualizerPlugin
from sok_graph_visualizer.api.service.DataSourceService import DataSourcePlugin

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        """
        initialize the plugin manager

        the manager keeps two registries in memory:
        1. Data source plugins
        2. Visualizer plugins

        these registries are populated when plugins are loaded.
        """
        self._data_sources = {}
        self._data_visualizers = {}

    def load_plugins(self):
        """
        discover and load plugins from python entry points

        this method:
        1. Clears any previously loaded plugins
        2. Loads data source plugins from the `graph.data_source` group
        3. Loads visualizer plugins from the `graph.visualizer` group
        4. Validates each plugin against its expected base class
        5. Registers valid plugins by their entry point name
        """
        self._data_sources.clear()
        self._data_visualizers.clear()

        ds_entry_points = entry_points(group="graph.data_source")
        for ep in ds_entry_points:
            try:
                if ep.name in self._data_sources:
                    logger.warning(f"duplicate id: {ep.name}, there ia already one like that, skip")
                    continue
                plugin_class = ep.load()
                self._validate_plugin(plugin_class, DataSourcePlugin, ep.name)
                self._data_sources[ep.name] = plugin_class
                logger.info(f"loaded data source plugin: {ep.name}")
            except Exception as e:
                logger.error(f"error while loading {ep.name}: {e}")
        
        dv_entry_points = entry_points(group="graph.visualizer")
        for ep in dv_entry_points:
            try:
                if ep.name in self._data_visualizers:
                    logger.warning(f"duplicate id: {ep.name}, there ia already one like that, skip")
                    continue
                plugin_class = ep.load()
                self._validate_plugin(plugin_class, VisualizerPlugin, ep.name)
                self._data_visualizers[ep.name] = plugin_class
                logger.info(f"loaded visualizer plugin: {ep.name}")
            except Exception as e:
                logger.error(f"error while loading {ep.name}: {e}")

    def _validate_plugin(self, plugin_class, base_class, name):
        """
        validate that a plugin implements the expected interface

        Args:
            plugin_class: The loaded plugin class.
            base_class: The abstract base class it must inherit.
            name: The entry point name used for error reporting.

        Raises:
            TypeError: If the plugin does not inherit from the base class.
        """
        if not issubclass(plugin_class, base_class):
            raise TypeError(f"Plugin '{name}' doesnt inherit {base_class.__name__}")

    def get_data_source_plugins(self) -> dict:
        """
        get all registered data source plugins.

        Returns:
            dict: Mapping of plugin name to plugin class.
        """
        return self._data_sources

    def get_visualizer_plugins(self) -> dict:
        """
        get all registered visualizer plugins

        Returns:
            dict: Mapping of plugin name to plugin class.
        """
        return self._data_visualizers

    def instantiate_data_source(self, name: str, **kwargs) -> DataSourcePlugin:
        """
        instantiate a data source plugin by name

        Args:
            name: Entry point name of the plugin to instantiate.
            **kwargs: Keyword arguments forwarded to the plugin constructor.

        Returns:
            DataSourceService: Instance of the requested data source plugin.

        Raises:
            ValueError: If no plugin with the given name is registered.
        """
        if name not in self._data_sources:
            raise ValueError(f"ds plugin '{name}' not found")
        return self._data_sources[name](**kwargs)

    def instantiate_visualizer(self, name: str, **kwargs) -> VisualizerPlugin:
        """
        instantiate a visualizer plugin by name

        Args:
            name: Entry point name of the plugin to instantiate.
            **kwargs: Keyword arguments forwarded to the plugin constructor.

        Returns:
            DataVisualizerService: Instance of the requested visualizer plugin.

        Raises:
            ValueError: If no plugin with the given name is registered.
        """
        if name not in self._data_visualizers:
            raise ValueError(f"dv plugin '{name}' not found")
        return self._data_visualizers[name](**kwargs)