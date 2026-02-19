# Vantablack Core v5 — Red Team Operations Suite (Clean Edition)

Vantablack Core v5 is a modular, research‑oriented framework for red‑team training and security experimentation. This “Clean” edition focuses on safe, lawful use with built‑in safeguards, local self‑audit flows, and clear guidance to prevent misuse.

> Important: Use only in environments you own or explicitly control, with proper authorization. The maintainers do not condone, encourage, or support illegal activity.

## Highlights

- Unified CLI (“vanta”) for workflows: diagnostics, demo API, mutation engine, edge demo.
- Edge Proxy (optional) for controlled experiments using mitmproxy, with:
  - Same‑origin “bridges” for assets/APIs,
  - Injection harness for JS rewriter and safe stubbing (e.g., WebAuthn),
  - Blocklists, header rules, and hardening profiles (default/stealth/strict/perf/parano).
- Phishlet loader (YAML) with legacy schema converter and catalog validation.
- Mutation + detection pipeline with a simple Autopilot.
- Safe‑mode local server for self‑audit without exfiltration.

## Quick Start

1) Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies:

```bash
python -m pip install -r requirements-v5.txt
```

3) **Red Team Operations (Full Scenario):**

Follow the 6-Phase Attack Plan detailed in `plan.md`.

**Phase 1: Reconnaissance**
```bash
vanta analyze --target @ceo_target --platform linkedin
```

**Phase 2 & 4: Weaponization & Capture**
```bash
vanta edge-run --path phishlets/linkedin.yaml --port 8443
```

**Phase 3: Distribution**
```bash
vanta safe-qr --url http://localhost:8443 --logo core/assets/logos/linkedin.png
```

**Phase 5: Access (Loot)**
```bash
vanta loot
```

## Ethical Use & Safety

- Legal boundaries: Use only with authorization and for defense training.
- No secret logging: The codebase avoids logging secrets by default.
- Safe‑mode: A local self‑audit server demonstrates flows entirely on localhost with no data exfiltration.
- Allow‑lists: A CLI audit validates YAML hosts against an allowlist to avoid accidental targeting of live domains.

### Safe‑Mode (Local, No Exfil)

Runs a local self‑audit site for demonstration on your own machine.

```bash
vanta safe-mode
```

This invokes the local server defined in `scripts/self_destruct.py`’s sibling `safe_mode.py` and opens your browser at http://localhost:8888. It is useful for awareness training and internal demos.

### Phishlets Audit (Allowlist)

Validate catalog entries against suffix allow‑lists:

```bash
vanta phishlets-audit --allow localhost,example.com
```

The audit prints a summary of hosts that fall outside of the provided suffix allow‑list.

## CLI Overview

```bash
vanta init                 # Initialize .env interactively
vanta doctor               # Environment diagnostics
vanta analyze              # OSINT Reconnaissance (Phase 1)
vanta safe-qr              # QR Code Generator (Phase 3)
vanta loot                 # Session/Credential Dump (Phase 5)
vanta demo                 # Launch demo API with metrics
vanta phishlets-list       # List available phishlets
vanta phishlets-validate   # Validate all phishlets
vanta safe-mode            # Local self-audit server (no exfil)
vanta phishlets-audit      # Check YAML hosts against an allow-list

# Edge demos (optional, mitmproxy required)
vanta edge-demo --phishlet phishlets/example.yaml
vanta edge-run  --name x --profile strict --port 8443
```

Edge profiles:
- `default`: baseline behavior,
- `stealth`: larger blocklist, removes NEL/Report‑To headers,
- `strict`: HTTP/2 off, aggressive blocklist + header removals,
- `perf`: permissive with light analytics filtering,
- `parano`: restrictive (images/video/fonts minimized), HTTP/2 off.

## Edge Proxy (Optional)

The Edge Proxy integrates with mitmproxy if installed. It supports “bridges” that rewrite absolute external URLs to same‑origin paths (e.g., `/ _gapi` → `apis.google.com`), client‑side injection to re‑route fetch/XHR, and response patching for CORS fallbacks. It is intended for controlled, lawful research only.

Key modules:
- Interceptor: request/response rewriting, injections, cookie rewriting, and basic credential/tokens scanning stubs.
- Phishlet Loader: pydantic schema for YAML entries plus a legacy converter.

## Phishlets

- Location: `phishlets/*.yaml`
- Fields include: `proxy_hosts`, `bridges`, `headers`, `path_rewrites`, `cookie_rewrites`, `blocklist`, and `form_actions`.
- Validation: `vanta phishlets-validate`
- Discovery: `vanta phishlets-list`

Always validate and test with the allow‑list audit before demonstrations.

## Development

### Project Layout (Key Paths)

- API & Guide: `core/api/routes.py`
- CLI: `core/cli/main.py`
- Edge Proxy: `core/edge/proxy.py`, `core/edge/interceptor.py`, `core/edge/phishlets.py`
- Mutation/Autopilot: `core/mutation/*`, `core/orchestrator/*`
- Safe Mode: `safe_mode.py`
- Self‑Destruct (guarded): `scripts/self_destruct.py`

### Tests

```bash
source .venv/bin/activate
pytest -q
```

### Coding Standards

- Keep changes minimal, explicit, and auditable.
- Do not commit secrets.
- Prefer allow‑lists and dry‑runs for potentially destructive operations.

## Troubleshooting

- mitmproxy missing: Edge demos will fail gracefully with instructions to install the optional dependency.
- 4xx/5xx responses: Differentiate upstream application responses from transport issues; CORS/bridges are handled by the interceptor, but upstream may still return expected access errors in demo contexts.
- Ports in use: Adjust `--port` or stop existing processes.

## Security Notes

- This code is for defensive research, awareness, and training with consent.
- Add organizational guardrails (IP allow‑lists, strict profiles, internal DNS) for demos.
- Consider a local OIDC sandbox if you need to validate authorize/token flows without targeting external services.

## License & Attribution

This repository is provided “as is” for lawful research and education. Verify licensing per your usage context and dependencies.

---

If you are uncertain whether a use case is allowed, do not proceed. When in doubt, run `vanta safe-mode` and keep experiments on localhost.

