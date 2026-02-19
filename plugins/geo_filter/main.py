import logging
from typing import Dict, Any

class GeoFilterPlugin:
    def __init__(self, api):
        self.api = api
        self.logger = api.get_logger("geo_filter")
        
        # Load config (could be from file, here hardcoded for demo)
        self.allowed_countries = ["US", "FR", "GB", "CA", "DE"] 
        
        # Register hooks
        # Priority 50 (NORMAL) - runs after Anti-Analysis (100)
        self.api.plugin_manager.hook_system.register_hook("http.request.intercept", self, self.check_geo)

    def check_geo(self, request: Dict[str, Any]) -> bool:
        """Check IP location against allowed countries"""
        ip = request.get("remote_addr", "")
        
        # Mock GeoIP lookup (In real deployment, use MaxMind DB or API)
        country = self._mock_geoip(ip)
        
        if country not in self.allowed_countries:
            self.logger.info(f"Blocked IP {ip} from {country} (Not in target list)")
            return False
            
        return True

    def _mock_geoip(self, ip: str) -> str:
        # Simple mock for local testing
        if ip.startswith("192.168.") or ip.startswith("10.") or ip == "127.0.0.1":
            return "US" # Local is allowed
        
        # In a real scenario, we would use a library like geoip2
        # import geoip2.database
        # reader = geoip2.database.Reader('GeoLite2-Country.mmdb')
        # response = reader.country(ip)
        # return response.country.iso_code
        
        return "US" # Default to US for now
