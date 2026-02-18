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
