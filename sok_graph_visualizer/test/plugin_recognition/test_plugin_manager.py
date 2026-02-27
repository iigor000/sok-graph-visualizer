"""
Test suite for PluginManager class.

Run Instructions:
    Navigate to the repository root and run python .\test\plugin_recognition\test_plugin_manager.py`    
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
import sys
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from api.service.DataSourceService import DataSourcePlugin
from api.service.DataVisualizerService import VisualizerPlugin
from core.plugin_recognition import PluginManager

class ValidDataSourceMock(DataSourcePlugin):
    """
    Mock data source plugin for testing.
    
    This class:
    1. Inherits from DataSourcePlugin to pass validation
    2. Stores constructor kwargs for assertion in tests
    3. Implements minimum required abstract methods
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    def get_name(self):
        return "Mock DS"

    def get_required_config(self):
        return []

    def parse(self):
        pass

class ValidVisualizerMock(VisualizerPlugin):
    """
    Mock visualizer plugin for testing.
    
    This class:
    1. Inherits from VisualizerPlugin to pass validation
    2. Stores constructor kwargs for assertion in tests
    3. Implements minimum required abstract methods
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_name(self):
        return "Mock DS"

    def get_description(self):
        return "Description"

    def render(self, graph):
        pass

class InvalidPluginMock:
    """
    Mock class for testing rejection of invalid plugins.
    
    This class:
    1. DOES NOT inherit from any API base class
    2. Will fail the PluginManager validation
    3. Used to test error handling for non-conforming plugins
    """
    pass

# TEST SUITE

class TestPluginManager(unittest.TestCase):
    """
    Test suite for the PluginManager class.
    
    This test class validates:
    1. Loading and registering valid plugins from entry points
    2. Rejecting invalid plugins that don't inherit from base classes
    3. Handling duplicate plugin IDs
    4. Instantiating plugins via factory methods
    5. Error handling for missing plugins
    """

    def setUp(self):
        """
        Initialize test environment before each test case.
        
        This method:
        1. Creates a fresh PluginManager instance for isolation
        2. Suppresses logging output for cleaner test output
        3. Ensures a clean slate for each test
        """
        self.manager = PluginManager()
        # we 'turn off' logger while testing
        logging.getLogger('core.plugin_recognition').setLevel(logging.CRITICAL)

    @patch('core.plugin_recognition.entry_points')
    def test_load_valid_plugins(self, mock_entry_points):
        """
        Verify that the manager correctly loads and registers valid plugins.
        
        This test:
        1. Mocks entry points for both data source and visualizer groups
        2. Mocks valid plugin classes that inherit from correct base classes
        3. Calls load_plugins() to trigger the discovery process
        4. Asserts that plugins are registered with correct names and classes
        
        Expected Result:
            Both data source and visualizer plugins are found and registered.
        """
        
        # arrange
        ds_ep = MagicMock()
        ds_ep.name = "mock_json_ds"
        ds_ep.load.return_value = ValidDataSourceMock

        dv_ep = MagicMock()
        dv_ep.name = "mock_simple_vis"
        dv_ep.load.return_value = ValidVisualizerMock

        def mock_ep_func(group):
            if group == "graph.data_source":
                return (ds_ep,)
            elif group == "graph.visualizer":
                return (dv_ep,)
            return ()
        
        mock_entry_points.side_effect = mock_ep_func

        # act
        self.manager.load_plugins()

        # assert
        ds_plugins = self.manager.get_data_source_plugins()
        dv_plugins = self.manager.get_visualizer_plugins()

        self.assertIn("mock_json_ds", ds_plugins)
        self.assertEqual(ds_plugins["mock_json_ds"], ValidDataSourceMock)
        
        self.assertIn("mock_simple_vis", dv_plugins)
        self.assertEqual(dv_plugins["mock_simple_vis"], ValidVisualizerMock)

    @patch('core.plugin_recognition.entry_points')
    def test_invalid_plugin_is_rejected(self, mock_entry_points):
        """
        Verify that plugins failing validation are rejected and not registered.
        
        This test:
        1. Mocks an entry point that returns a class not inheriting from API base
        2. Calls load_plugins() to attempt loading the invalid plugin
        3. Asserts that both plugin registries remain empty (plugin was rejected)
        
        Expected Result:
            Invalid plugins are silently skipped, registries stay empty.
        """
        
        bad_ep = MagicMock()
        bad_ep.name = "bad_plugin"
        bad_ep.load.return_value = InvalidPluginMock

        mock_entry_points.return_value = (bad_ep,)

        self.manager.load_plugins()

        # they need to be empty
        self.assertEqual(len(self.manager.get_data_source_plugins()), 0)
        self.assertEqual(len(self.manager.get_visualizer_plugins()), 0)

    @patch('core.plugin_recognition.entry_points')
    def test_duplicate_plugin_id_is_skipped(self, mock_entry_points):
        """
        Verify that duplicate plugin IDs are detected and only the first is kept.
        
        This test:
        1. Mocks two entry points with the same name in the same category
        2. Calls load_plugins() to process both
        3. Asserts that only one plugin is registered (duplicate was skipped)
        
        Expected Result:
            Registry contains exactly 1 plugin; the second duplicate was ignored.
        """
        
        ep1 = MagicMock()
        ep1.name = "duplicate_id"
        ep1.load.return_value = ValidDataSourceMock

        ep2 = MagicMock()
        ep2.name = "duplicate_id"
        ep2.load.return_value = ValidDataSourceMock

        # two plugs with same ep
        mock_entry_points.side_effect = lambda group: (ep1, ep2) if group == "graph.data_source" else ()

        self.manager.load_plugins()

        ds_plugins = self.manager.get_data_source_plugins()
        # only one needs to be added
        self.assertEqual(len(ds_plugins), 1)

    def test_instantiate_plugins(self):
        """
        Verify that the factory methods correctly instantiate registered plugins.
        
        This test:
        1. Manually registers mock plugin classes in manager registries
        2. Calls instantiate_data_source() and instantiate_visualizer() factory methods
        3. Passes custom keyword arguments to verify they are forwarded
        4. Asserts that returned instances are of correct type and have correct kwargs
        
        Expected Result:
            Factory methods create properly configured instances with forwarded arguments.
        """
        
        self.manager._data_sources["test_ds"] = ValidDataSourceMock
        self.manager._data_visualizers["test_dv"] = ValidVisualizerMock

        ds_instance = self.manager.instantiate_data_source("test_ds", path="test.json")
        dv_instance = self.manager.instantiate_visualizer("test_dv", color="red")

        self.assertIsInstance(ds_instance, ValidDataSourceMock)
        self.assertEqual(ds_instance.kwargs.get("path"), "test.json")

        self.assertIsInstance(dv_instance, ValidVisualizerMock)
        self.assertEqual(dv_instance.kwargs.get("color"), "red")

    def test_instantiate_missing_plugin_raises_value_error(self):
        """
        Verify that attempting to instantiate non-existent plugins raises ValueError.
        
        This test:
        1. Calls instantiate_data_source() with a name not in the registry
        2. Calls instantiate_visualizer() with a name not in the registry
        3. Asserts that both raise ValueError with appropriate message
        
        Expected Result:
            ValueError is raised when requesting a non-registered plugin.
        """
        
        with self.assertRaises(ValueError):
            self.manager.instantiate_data_source("nepostojeci_plugin")

        with self.assertRaises(ValueError):
            self.manager.instantiate_visualizer("nepostojeci_plugin")

if __name__ == '__main__':
    unittest.main()