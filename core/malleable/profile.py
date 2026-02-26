"""
Vantablack Core v5 - Malleable C2 Profile Manager
=================================================

This module loads and manages Malleable C2 profiles.
"""

import yaml
from typing import Dict, Any

class MalleableProfile:
    """
    Represents a Malleable C2 profile, providing access to its configuration.
    """
    def __init__(self, profile_path: str):
        self.profile_path = profile_path
        self.config = self._load_profile()

    def _load_profile(self) -> Dict[str, Any]:
        """Loads the YAML profile from the given path."""
        try:
            with open(self.profile_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ValueError(f"Malleable profile not found at: {self.profile_path}")
        except Exception as e:
            raise ValueError(f"Error loading malleable profile: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Retrieves a value from the profile using a dot-separated key path.
        Example: 'http-config.headers.Server'
        """
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

# Global instance to be used throughout the application
# This can be initialized at startup with a specific profile.
malleable_profile = None

def load_malleable_profile(profile_name: str = "default"):
    """
    Initializes the global malleable_profile instance.
    """
    global malleable_profile
    profile_path = f"profiles/malleable/{profile_name}.yml"
    malleable_profile = MalleableProfile(profile_path)
    print(f"[INFO] Malleable C2 profile '{profile_name}' loaded.")

