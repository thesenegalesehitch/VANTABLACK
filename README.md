# Vantablack Core v5 — Red Team Operations Suite (Clean Edition)

Vantablack Core v5 is a modular, research‑oriented framework for red‑team training and security experimentation. This “Clean” edition focuses on safe, lawful use with built‑in safeguards, local self‑audit flows, and clear guidance to prevent misuse.

> Important: Use only in environments you own or explicitly control, with proper authorization. The maintainers do not condone, encourage, or support illegal activity.

## Faits marquants

- Templates haute fidélité et comportements réalistes (Google, Microsoft, etc.).
- Relais de session en temps réel (AiTM) côté serveur.
- Furtivité avancée (anti‑bot, mobile‑only, anti‑analyse client).
- Internationalisation terminal (en/fr).
- Prêt pour WAN via Cloudflared.

## Démarrage rapide

1) Environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Dépendances :

```bash
python -m pip install -r requirements.txt
```

3) Bootstrap multi-OS (création venv + vérifs) :

```bash
python scripts/bootstrap.py
```

4) Lancer une attaque locale + tunnel :

```bash
python3 run_real_attack.py --target google --stealth
# Le script détecte cloudflared et publie un lien WAN trycloudflare.com
```

5) Générer un QR (Quishing) :
```bash
python3 quishing.py --url https://votre-lure.trycloudflare.com/login --logo core/assets/logos/google.png --lang fr
```

## Validation automatique (Local & WAN)

```bash
python3 scripts/validate_targets.py
# Pour chaque cible : démarre le serveur local, vérifie /health et /login.
# Si Cloudflared est installé, vérifie aussi l’URL WAN.
```

## Commandes utiles

```bash
python3 phishing_server.py --target microsoft --port 8080 --stealth --lang fr
python3 run_real_attack.py --target twitter --geo
```

## Bonnes pratiques

- Legal boundaries: Use only with authorization and for defense training.
- No secret logging: The codebase avoids logging secrets by default.
- Allow‑lists: Audit local avant démo publique.

## CLI Overview

```bash
vanta init
vanta doctor
vanta phishlets-list
vanta phishlets-validate
# Edge (optionnel, mitmproxy requis)
vanta edge-run --name x --profile strict --port 8443
```

Profils Edge (optionnel) :
- `default`: baseline behavior,
- `stealth`: larger blocklist, removes NEL/Report‑To headers,
- `strict`: HTTP/2 off, aggressive blocklist + header removals,
- `perf`: permissive with light analytics filtering,
- `parano`: restrictive (images/video/fonts minimized), HTTP/2 off.

## Edge Proxy (Optionnel)

Intégration mitmproxy pour recherches avancées (si installé). À utiliser uniquement dans un cadre légal et contrôlé.

Modules clés :
- Interceptor : réécriture requêtes/réponses, injections, cookies.
- Phishlet Loader : schéma YAML et convertisseur legacy.

## Phishlets

- Location: `phishlets/*.yaml`
- Fields include: `proxy_hosts`, `bridges`, `headers`, `path_rewrites`, `cookie_rewrites`, `blocklist`, and `form_actions`.
- Validation: `vanta phishlets-validate`
- Discovery: `vanta phishlets-list`

Toujours valider en interne avant démonstration.

## Development

### Structure (Clé)

- CLI: `core/cli/main.py`
- Edge Proxy: `core/edge/proxy.py`, `core/edge/interceptor.py`, `core/edge/phishlets.py`
- Serveur phishing: `phishing_server.py`
- Templates: `core/assets/templates/high_fidelity/*`
- I18n: `core/locales/*`, `core/utils/i18n.py`
- Quishing: `quishing.py`
- Validation: `scripts/validate_targets.py`

### Tests rapides

```bash
source .venv/bin/activate
pytest -q
```

### Règles de commits (Conventional Commits)

```bash
git config core.hooksPath .githooks
# Exemple valide : feat(core): add health endpoint
```

### Standards de code

- Keep changes minimal, explicit, and auditable.
- Do not commit secrets.
- Prefer allow‑lists and dry‑runs for potentially destructive operations.

## Troubleshooting

- mitmproxy absent: edge non disponible (optionnel).
- 4xx/5xx : différencier erreurs amont et transport.
- Port occupé : ajuster `--port` ou arrêter les processus.

## Security Notes

- This code is for defensive research, awareness, and training with consent.
- Add organizational guardrails (IP allow‑lists, strict profiles, internal DNS) for demos.
- Consider a local OIDC sandbox if you need to validate authorize/token flows without targeting external services.

## License & Attribution

This repository is provided “as is” for lawful research and education. Verify licensing per your usage context and dependencies.

---

If you are uncertain whether a use case is allowed, do not proceed. Keep experiments on localhost.
