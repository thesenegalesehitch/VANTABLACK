"""
Vantablack Core v5 - Dashboard API
==================================

Endpoints for:
- Real-time Campaign Status
- Phishlet Management
- Metrics Export (Prometheus)
"""

from fastapi import APIRouter, HTTPException, Response, Request
from typing import Dict, List
from core.common.metrics import MetricsManager
from core.common.config import sanitized

router = APIRouter(prefix="/v5", tags=["Vantablack Core"])

@router.get("/health")
async def health_check():
    """System Health Check"""
    return {"status": "operational", "version": "5.0.0-hyperdrive"}

@router.get("/metrics")
async def metrics():
    """Prometheus Metrics Export"""
    data, content_type = MetricsManager.get_latest_metrics()
    return Response(content=data, media_type=content_type)

@router.get("/config")
async def get_config():
    return {"config": sanitized()}

@router.get("/campaigns")
async def list_campaigns():
    """List active campaigns (Mock)"""
    # TODO: Connect to Orchestrator state
    return {
        "active": 2,
        "campaigns": [
            {"id": "camp_001", "target": "internal_test", "status": "running"},
            {"id": "camp_002", "target": "red_team_ops", "status": "paused"}
        ]
    }

@router.post("/mutation/preview")
async def preview_mutation(payload: Dict[str, str]):
    """
    Test mutation engine via API
    Payload: {"html": "..."}
    """
    from core.mutation.engine import MutationEngine
    engine = MutationEngine()
    
    if "html" in payload:
        return {"mutated": engine.mutate_html(payload["html"])}
    
    raise HTTPException(status_code=400, detail="Invalid payload")

@router.get("/guide")
async def guide():
    html = """
    <html>
      <head><title>Vantablack v5 Guide</title></head>
      <body>
        <h1>Vantablack Core v5</h1>
        <h2>Getting Started</h2>
        <ol>
          <li>pip install -r requirements-v5.txt</li>
          <li>vanta demo</li>
          <li>Open /v5/guide and /v5/metrics</li>
        </ol>
        <h2>CLI</h2>
        <ul>
          <li>vanta init</li>
          <li>vanta doctor</li>
          <li>vanta mutate --file file.html</li>
          <li>vanta analyze --file file.html</li>
        </ul>
        <h2>APIs</h2>
        <ul>
          <li>/v5/health</li>
          <li>/v5/metrics</li>
          <li>/v5/config</li>
          <li>/v5/mutation/preview</li>
        </ul>
      </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
