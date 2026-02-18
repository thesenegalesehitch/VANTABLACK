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
async def guide(page: str = "home"):
    pages = {
        "home": """
          <section>
            <h2>Démarrage Express</h2>
            <ol>
              <li>python3 -m venv .venv && source .venv/bin/activate</li>
              <li>python -m pip install -r requirements-v5.txt</li>
              <li>python -m core.cli.main demo</li>
              <li>Voir <a href="/v5/metrics">/v5/metrics</a> et <a href="/v5/guide?page=cli">CLI</a></li>
            </ol>
          </section>
        """,
        "cli": """
          <section>
            <h2>CLI</h2>
            <pre>
vanta init           # Crée .env
vanta doctor         # Diagnostics
vanta demo           # Lance API demo
vanta mutate --file payload.html
vanta analyze --file payload.html
vanta edge-demo --phishlet phishlets/example.yaml   # si mitmproxy installé
vanta lunar          # Mode avancé (mutation+scanner+autopilot)
vanta edge-run --name google --profile stealth --rate 60 --deny-ips 1.2.3.4
            </pre>
          </section>
        """,
        "delivery": """
          <section>
            <h2>Delivery</h2>
            <p>SMTP asynchrone via aiosmtplib. Fallbacks pour le rendu MJML/texte.</p>
          </section>
        """,
        "edge": """
          <section>
            <h2>Edge</h2>
            <p>Proxy MitM optionnel basé sur mitmproxy. Démo activable via CLI si dépendance présente.</p>
          </section>
        """,
        "mutation": """
          <section>
            <h2>Mutation & Autopilot</h2>
            <p>Moteur polymorphe (HTML/JS) + Scanner statique + cycle AutoPilot.</p>
          </section>
        """,
        "phishlets": """
          <section>
            <h2>Phishlets</h2>
            <p>Catalogue: x, google, microsoft, github, facebook, linkedin, paypal, preset_demo.</p>
            <pre>
vanta phishlets-list
vanta edge-run --name x
vanta edge-run --name google
vanta edge-run --name microsoft
vanta edge-run --name github
vanta edge-run --name facebook
vanta edge-run --name linkedin
vanta edge-run --name paypal
            </pre>
          </section>
        """,
        "ethics": """
          <section>
            <h2>Éthique & Sécurité</h2>
            <ul>
              <li>Ne jamais utiliser hors cadre légal.</li>
              <li>Ne jamais loguer de secrets.</li>
              <li>Limiter l'exposition réseau en démo.</li>
              <li>Préférer les environnements simulés (sandbox) pour l'entraînement.</li>
            </ul>
            <h3>Mode Sécurisé</h3>
            <pre>vanta safe-mode</pre>
            <p>Audit visuel local (localhost). Aucune exfiltration.</p>
          </section>
        """,
        "network": """
          <section>
            <h2>Réseau</h2>
            <ul>
              <li>Limiteur: RATE_LIMIT_PER_MINUTE (def: 120)</li>
              <li>ACL: ALLOW_IPS, DENY_IPS (CSV d'IP)</li>
              <li>Proxy amont: UPSTREAM_HTTP (ex: http://user:pass@host:3128)</li>
              <li>HTTP/2 & stratégie connexion configurables dans EdgeConfig</li>
            </ul>
            <p>Edge demo: <code>python -m core.cli.main edge-demo --port 8443</code></p>
          </section>
        """
    }

    # Dynamic listing for phishlets page
    dynamic_section = ""
    if page == "phishlets":
        try:
            import os, yaml
            entries = []
            for fn in os.listdir("phishlets"):
                if fn.endswith(".yaml"):
                    with open(os.path.join("phishlets", fn), "r") as f:
                        data = yaml.safe_load(f)
                    name = data.get("name", fn[:-5])
                    entries.append(f"- {fn[:-5]} → {name}")
            if entries:
                dynamic_section = "<h3>Catalogue détecté</h3><pre>" + "\\n".join(entries) + "</pre>"
        except Exception:
            pass
        pages["phishlets"] = pages["phishlets"].replace("</section>", dynamic_section + "</section>")

    nav = """
      <nav>
        <a href="/v5/guide?page=home">Accueil</a>
        <a href="/v5/guide?page=cli">CLI</a>
        <a href="/v5/guide?page=delivery">Delivery</a>
        <a href="/v5/guide?page=edge">Edge</a>
        <a href="/v5/guide?page=mutation">Mutation</a>
        <a href="/v5/guide?page=phishlets">Phishlets</a>
        <a href="/v5/guide?page=network">Réseau</a>
        <a href="/v5/guide?page=ethics">Éthique</a>
      </nav>
    """
    content = pages.get(page, pages["home"])
    html = f"""
    <html>
      <head>
        <title>Vantablack v5 Guide</title>
        <style>
          body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto; margin: 0; padding: 0; }}
          header {{ background: #0b0b0b; color: #fff; padding: 16px; }}
          nav a {{ margin-right: 12px; color: #0b0b0b; text-decoration: none; font-weight: 600; }}
          nav {{ background: #f5f5f7; padding: 8px 16px; border-bottom: 1px solid #e5e5e7; }}
          main {{ padding: 24px; }}
          pre {{ background: #0f0f14; color: #e6e6e6; padding: 16px; border-radius: 8px; overflow-x: auto; }}
          a {{ color: #0070f3; }}
        </style>
      </head>
      <body>
        <header><h1>Vantablack Core v5 - Guide</h1></header>
        {nav}
        <main>{content}</main>
      </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
