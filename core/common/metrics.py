"""
Vantablack Core v5 - Metrics & Observability
============================================

Handles Prometheus export and internal health tracking.
"""

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict

# Metrics Definitions
REQUEST_COUNT = Counter('vanta_request_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
CAMPAIGN_STATUS = Gauge('vanta_campaign_active', 'Active Campaigns')
PHISHLET_LOAD = Gauge('vanta_phishlet_loaded', 'Loaded Phishlets')
MUTATION_OPS = Counter('vanta_mutation_total', 'Total Mutations Performed')
DETECTION_EVENTS = Counter('vanta_detection_events', 'Detected Blocking Events')
RATE_LIMITED = Counter('vanta_rate_limited_total', 'Requests rate-limited', ['ip'])
BLOCKED_IP = Counter('vanta_blocked_ip_total', 'Requests blocked by ACL', ['ip'])

class MetricsManager:
    @staticmethod
    def record_request(method: str, endpoint: str, status: int):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()

    @staticmethod
    def set_campaign_count(count: int):
        CAMPAIGN_STATUS.set(count)

    @staticmethod
    def get_latest_metrics():
        return generate_latest(), CONTENT_TYPE_LATEST

    @staticmethod
    def get_all_metrics():
        """Return all metrics as a dictionary for API responses."""
        # For prometheus_client metrics, we need to collect them differently
        from prometheus_client import generate_latest
        from io import BytesIO
        
        # Generate metrics output and parse it
        metrics_data = generate_latest().decode('utf-8')
        metrics_dict = {}
        
        for line in metrics_data.split('\n'):
            if line and not line.startswith('#'):
                if 'vanta_request_total' in line:
                    metrics_dict['request_total'] = float(line.split()[-1])
                elif 'vanta_campaign_active' in line:
                    metrics_dict['campaign_active'] = float(line.split()[-1])
                elif 'vanta_phishlet_loaded' in line:
                    metrics_dict['phishlet_loaded'] = float(line.split()[-1])
                elif 'vanta_mutation_total' in line:
                    metrics_dict['mutation_total'] = float(line.split()[-1])
                elif 'vanta_detection_events' in line:
                    metrics_dict['detection_events'] = float(line.split()[-1])
                elif 'vanta_rate_limited_total' in line:
                    metrics_dict['rate_limited_total'] = float(line.split()[-1])
                elif 'vanta_blocked_ip_total' in line:
                    metrics_dict['blocked_ip_total'] = float(line.split()[-1])
        
        return metrics_dict
