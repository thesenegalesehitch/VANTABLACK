"""
Vantablack C2 Plugin System
Modular plugin architecture for extending C2 capabilities.
"""

import importlib
import inspect
from typing import Dict, List, Optional, Any, Type, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

from .exceptions import PluginError

logger = logging.getLogger(__name__)

class PluginCapability(Enum):
    """Enum representing plugin capabilities."""
    LATERAL_MOVEMENT = "lateral_movement"
    PERSISTENCE = "persistence" 
    DEFENSE_EVASION = "defense_evasion"
    EXFILTRATION = "exfiltration"
    RECONNAISSANCE = "reconnaissance"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    CUSTOM = "custom"

@dataclass
class PluginMetadata:
    """Metadata for a Vantablack plugin."""
    name: str
    version: str = "1.0.0"
    author: str = "Unknown"
    description: str = ""
    capabilities: Set[PluginCapability] = field(default_factory=set)
    min_c2_version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'capabilities': [cap.value for cap in self.capabilities],
            'min_c2_version': self.min_c2_version
        }

class VantaPlugin:
    """
    Base class for all Vantablack C2 plugins.
    
    Plugins extend the core C2 functionality with additional capabilities
    such as lateral movement, persistence, defense evasion, etc.
    """
    
    def __init__(self):
        self.metadata = PluginMetadata(
            name=self.__class__.__name__,
            capabilities={
                PluginCapability.LATERAL_MOVEMENT,
                PluginCapability.PERSISTENCE,
                PluginCapability.DEFENSE_EVASION
            }
        )
        self.enabled: bool = True
        self.config: Dict[str, Any] = {}
    
    async def initialize(self, config: Dict[str, Any] = None) -> None:
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
            
        Raises:
            PluginError: If initialization fails
        """
        try:
            self.config = config or {}
            logger.info(f"Initialized plugin {self.metadata.name}")
            
        except Exception as e:
            raise PluginError(self.metadata.name, f"Initialization failed: {e}")
    
    async def execute(self, command: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a plugin command.
        
        Args:
            command: Command to execute
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Command execution results
            
        Raises:
            PluginError: If command execution fails
        """
        try:
            method_name = f"cmd_{command}"
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                if inspect.iscoroutinefunction(method):
                    result = await method(**(args or {}))
                else:
                    result = method(**(args or {}))
                return result
            else:
                raise PluginError(self.metadata.name, f"Unknown command: {command}")
                
        except Exception as e:
            raise PluginError(self.metadata.name, f"Command execution failed: {e}")
    
    async def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        Raises:
            PluginError: If cleanup fails
        """
        try:
            logger.info(f"Cleaned up plugin {self.metadata.name}")
            
        except Exception as e:
            raise PluginError(self.metadata.name, f"Cleanup failed: {e}")
    
    # Example plugin commands
    async def cmd_lateral_move(self, target: str, technique: str = "wmi") -> Dict[str, Any]:
        """
        Perform lateral movement to a target host.
        
        Args:
            target: Target hostname or IP
            technique: Movement technique to use
            
        Returns:
            Dict[str, Any]: Movement results
        """
        return {
            'success': True,
            'target': target,
            'technique': technique,
            'message': f"Lateral movement to {target} using {technique}"
        }
    
    async def cmd_establish_persistence(self, method: str = "scheduled_task") -> Dict[str, Any]:
        """
        Establish persistence on the target.
        
        Args:
            method: Persistence method to use
            
        Returns:
            Dict[str, Any]: Persistence results
        """
        return {
            'success': True,
            'method': method,
            'message': f"Established persistence using {method}"
        }
    
    async def cmd_evade_defenses(self, technique: str = "amsi_bypass") -> Dict[str, Any]:
        """
        Evade defenses on the target.
        
        Args:
            technique: Evasion technique to use
            
        Returns:
            Dict[str, Any]: Evasion results
        """
        return {
            'success': True,
            'technique': technique,
            'message': f"Evaded defenses using {technique}"
        }

class PluginManager:
    """
    Manager for loading and controlling Vantablack plugins.
    """
    
    def __init__(self):
        self.plugins: Dict[str, VantaPlugin] = {}
        self.plugin_dir: Path = Path("plugins")
    
    async def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> VantaPlugin:
        """
        Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            config: Plugin configuration
            
        Returns:
            VantaPlugin: Loaded plugin instance
            
        Raises:
            PluginError: If plugin loading fails
        """
        try:
            # Try to import the plugin module
            module_name = f"plugins.{plugin_name}"
            module = importlib.import_module(module_name)
            
            # Find plugin class (should be named same as plugin)
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, VantaPlugin) and 
                    obj != VantaPlugin):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise PluginError(plugin_name, "No valid plugin class found")
            
            # Create and initialize plugin
            plugin = plugin_class()
            await plugin.initialize(config)
            
            self.plugins[plugin_name] = plugin
            logger.info(f"Loaded plugin {plugin_name}")
            
            return plugin
            
        except ImportError:
            raise PluginError(plugin_name, "Plugin module not found")
        except Exception as e:
            raise PluginError(plugin_name, f"Failed to load plugin: {e}")
    
    async def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Raises:
            PluginError: If plugin unloading fails
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            raise PluginError(plugin_name, "Plugin not loaded")
        
        try:
            await plugin.cleanup()
            del self.plugins[plugin_name]
            logger.info(f"Unloaded plugin {plugin_name}")
            
        except Exception as e:
            raise PluginError(plugin_name, f"Failed to unload plugin: {e}")
    
    async def execute_plugin_command(self, plugin_name: str, command: str, 
                                    args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a command on a plugin.
        
        Args:
            plugin_name: Name of the plugin
            command: Command to execute
            args: Command arguments
            
        Returns:
            Dict[str, Any]: Command execution results
            
        Raises:
            PluginError: If plugin or command not found
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            raise PluginError(plugin_name, "Plugin not loaded")
        
        try:
            return await plugin.execute(command, args)
            
        except Exception as e:
            raise PluginError(plugin_name, f"Command execution failed: {e}")
    
    def get_loaded_plugins(self) -> List[Dict[str, Any]]:
        """
        Get list of all loaded plugins with metadata.
        
        Returns:
            List[Dict[str, Any]]: List of plugin metadata
        """
        return [
            {
                'name': plugin.metadata.name,
                'version': plugin.metadata.version,
                'enabled': plugin.enabled,
                'capabilities': [cap.value for cap in plugin.metadata.capabilities]
            }
            for plugin in self.plugins.values()
        ]
    
    def get_plugin(self, plugin_name: str) -> Optional[VantaPlugin]:
        """
        Get a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to get
            
        Returns:
            Optional[VantaPlugin]: Plugin instance if found
        """
        return self.plugins.get(plugin_name)
    
    async def reload_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> VantaPlugin:
        """
        Reload a plugin with new configuration.
        
        Args:
            plugin_name: Name of the plugin to reload
            config: New plugin configuration
            
        Returns:
            VantaPlugin: Reloaded plugin instance
            
        Raises:
            PluginError: If plugin reloading fails
        """
        await self.unload_plugin(plugin_name)
        return await self.load_plugin(plugin_name, config)
    
    async def cleanup_all(self) -> None:
        """
        Cleanup all loaded plugins.
        
        Raises:
            PluginError: If cleanup fails for any plugin
        """
        errors = []
        for plugin_name in list(self.plugins.keys()):
            try:
                await self.unload_plugin(plugin_name)
            except Exception as e:
                errors.append(f"{plugin_name}: {e}")
        
        if errors:
            raise PluginError("cleanup_all", f"Failed to cleanup plugins: {', '.join(errors)}")