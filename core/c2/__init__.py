"""
Vantablack C2 Module - Command & Control Core
Enterprise-grade C2 infrastructure for advanced red team operations.
"""

__version__ = "1.0.0"
__author__ = "Vantablack Security Team"

from .core import VantaC2, Beacon, Listener
from .plugins import VantaPlugin, PluginManager
from .exceptions import C2Error, BeaconError, ListenerError

__all__ = [
    'VantaC2',
    'Beacon',
    'Listener',
    'VantaPlugin', 
    'PluginManager',
    'C2Error',
    'BeaconError',
    'ListenerError'
]