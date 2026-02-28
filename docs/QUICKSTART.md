# Quickstart

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Lancer l’UI
```bash
python -m uvicorn core.web.server:create_app --reload --port 8000
# http://localhost:8000/ui
```

## API V5 utile
- /v5/health
- /v5/config
- /v5/guide
- /v5/r/{campaign_id}
- /v5/phish/{campaign_id}/login?sid=…
- /v5/p/{session_id}/…
- /v5/session/{session_id}/export?format=json|netscape

## Tests & Qualité
```bash
pytest core/tests -q
mypy core/ --ignore-missing-imports
bandit -q -r core -x core/assets,core/web/static
```
