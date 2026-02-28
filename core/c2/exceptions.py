"""
C2 Module Exceptions
Custom exceptions for the Vantablack C2 system.
"""

class C2Error(Exception):
    """Base exception for all C2-related errors."""
    pass

class BeaconError(C2Error):
    """Exception raised for beacon-related operations."""
    def __init__(self, beacon_id: str, message: str):
        self.beacon_id = beacon_id
        self.message = message
        super().__init__(f"Beacon {beacon_id}: {message}")

class ListenerError(C2Error):
    """Exception raised for listener-related operations."""
    def __init__(self, listener_id: str, message: str):
        self.listener_id = listener_id
        self.message = message
        super().__init__(f"Listener {listener_id}: {message}")

class PluginError(C2Error):
    """Exception raised for plugin-related operations."""
    def __init__(self, plugin_name: str, message: str):
        self.plugin_name = plugin_name
        self.message = message
        super().__init__(f"Plugin {plugin_name}: {message}")

class AuthenticationError(C2Error):
    """Exception raised for authentication failures."""
    pass

class AuthorizationError(C2Error):
    """Exception raised for authorization failures."""
    pass

class CommunicationError(C2Error):
    """Exception raised for communication failures."""
    def __init__(self, target: str, message: str):
        self.target = target
        self.message = message
        super().__init__(f"Communication with {target} failed: {message}")

class ConfigurationError(C2Error):
    """Exception raised for configuration errors."""
    pass