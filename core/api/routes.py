"""
Vantablack Core v5 - Dashboard API
==================================

Endpoints for:
- Real-time Campaign Status
- Phishlet Management
- Metrics Export (Prometheus)
"""

from fastapi import APIRouter, HTTPException, Response
from typing import Dict, List
from core.common.metrics import MetricsManager

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
