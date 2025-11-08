"""Plugin manager for dynamic plugin loading and management."""

import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger


class PluginManager:
    """
    Manages plugins for the Cosik agent.
    Provides auto-discovery, loading, and lifecycle management.
    """
    
    def __init__(self, config, plugins_dir: str = "./src/plugins"):
        """
        Initialize plugin manager.
        
        Args:
            config: Configuration object
            plugins_dir: Directory containing plugins
        """
        self.config = config
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Any] = {}
        self.plugin_metadata: Dict[str, Dict] = {}
        
        logger.info(f"Plugin manager initialized with directory: {self.plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins in the plugins directory.
        
        Returns:
            List of plugin names
        """
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []
        
        plugin_names = []
        
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.stem.startswith('_'):
                continue
            
            if file_path.stem == '__init__':
                continue
            
            plugin_names.append(file_path.stem)
        
        logger.info(f"Discovered {len(plugin_names)} plugins: {plugin_names}")
        return plugin_names
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            True if loaded successfully
        """
        try:
            # Import plugin module
            module_path = f"src.plugins.{plugin_name}"
            module = importlib.import_module(module_path)
            
            # Check for PLUGIN_INFO
            if not hasattr(module, 'PLUGIN_INFO'):
                logger.warning(f"Plugin {plugin_name} missing PLUGIN_INFO")
                return False
            
            plugin_info = module.PLUGIN_INFO
            
            # Validate plugin info
            if 'name' not in plugin_info or 'class' not in plugin_info:
                logger.error(f"Plugin {plugin_name} has invalid PLUGIN_INFO")
                return False
            
            # Instantiate plugin class
            plugin_class = plugin_info['class']
            plugin_instance = plugin_class(self.config)
            
            # Store plugin
            self.plugins[plugin_info['name']] = plugin_instance
            self.plugin_metadata[plugin_info['name']] = {
                'version': plugin_info.get('version', '1.0.0'),
                'description': plugin_info.get('description', ''),
                'author': plugin_info.get('author', ''),
                'module': plugin_name
            }
            
            logger.info(f"Loaded plugin: {plugin_info['name']} v{plugin_info.get('version', '1.0.0')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> int:
        """
        Load all discovered plugins.
        
        Returns:
            Number of plugins loaded
        """
        plugin_names = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in plugin_names:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        logger.info(f"Loaded {loaded_count}/{len(plugin_names)} plugins")
        return loaded_count
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if unloaded successfully
        """
        if plugin_name not in self.plugins:
            logger.warning(f"Plugin {plugin_name} not loaded")
            return False
        
        try:
            # Call cleanup if available
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
            
            # Remove from loaded plugins
            del self.plugins[plugin_name]
            del self.plugin_metadata[plugin_name]
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Get a loaded plugin instance.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all loaded plugins with metadata.
        
        Returns:
            List of plugin information
        """
        plugins_list = []
        
        for name, metadata in self.plugin_metadata.items():
            plugins_list.append({
                'name': name,
                **metadata
            })
        
        return plugins_list
    
    async def execute_plugin(self, plugin_name: str, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a command on a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            command: Command to execute
            **kwargs: Additional arguments
            
        Returns:
            Execution result
        """
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            return {
                'success': False,
                'error': f'Plugin {plugin_name} not found'
            }
        
        try:
            # Check if plugin has execute method
            if hasattr(plugin, 'execute'):
                result = await plugin.execute(command, **kwargs)
                return result
            else:
                return {
                    'success': False,
                    'error': f'Plugin {plugin_name} does not have execute method'
                }
        except Exception as e:
            logger.error(f"Plugin execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_plugin_capabilities(self, plugin_name: str) -> List[str]:
        """
        Get capabilities/commands supported by a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List of supported commands
        """
        plugin = self.get_plugin(plugin_name)
        
        if not plugin:
            return []
        
        if hasattr(plugin, 'get_capabilities'):
            return plugin.get_capabilities()
        
        # Introspect methods
        capabilities = []
        for method_name in dir(plugin):
            if method_name.startswith('_'):
                continue
            
            method = getattr(plugin, method_name)
            if callable(method):
                capabilities.append(method_name)
        
        return capabilities
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin (useful for development).
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            True if reloaded successfully
        """
        if plugin_name in self.plugins:
            module_name = self.plugin_metadata[plugin_name]['module']
            self.unload_plugin(plugin_name)
        else:
            # Find module name from file
            module_name = plugin_name
        
        return self.load_plugin(module_name)
