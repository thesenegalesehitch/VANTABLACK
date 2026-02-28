# 🏗️ Architecture Technique Avancée - Vantablack Core v5

## 🧩 Modules Principaux

### 🔀 **SmartRedirector** (`core/redirect/smart_redirector.py`)
- **Filtrage Intelligent** : Détection bots/UA/IP en temps réel
- **Fingerprinting Polymorphique** : Collecte d'empreintes navigateur avancées
- **Routage Adaptatif** : Décision template vs AiTM basée sur le contexte
- **Session Management** : Création et suivi des sessions utilisateur

### 🎭 **AiTM Proxy** (`core/proxy/aitm.py`)
- **Man-in-the-Middle Avancé** : Interception HTTP/HTTPS/WebSocket
- **Réécriture Dynamique** : Modification des liens et contenus en vol
- **Capture Complète** : Cookies, tokens, credentials, sessions MFA
- **Furtivité** : Indétectabilité avancée avec signature TLS personnalisée

### 💾 **Session Manager** (`core/session/session_manager.py`)
- **Stockage Distribué** : Redis-based avec persistance optionnelle
- **Export Multi-format** : JSON, Puppeteer, Netscape, HAR
- **Chiffrement** : Données sensibles encryptées au repos
- **API RESTful** : Gestion programmatique des sessions

### 🖥️ **Web UI & Dashboard** (`core/web/server.py`)
- **Framework FastAPI** : Performances asynchrones optimisées
- **Middleware de Sécurité** : Authentification Tier2 (X-Vantablack-Auth)
- **Monitoring Temps Réel** : WebSocket pour updates live
- **Interface Responsive** : Compatible desktop/mobile

### 🔌 **API V5** (`core/api/routes.py`)
- **RESTful Design** : Endpoints structurés et documentés
- **Rate Limiting** : Protection contre les abus automatisés
- **Validation Stricte** : Schema validation avec Pydantic
- **Versioning** : Support multi-versions pour la compatibilité

### ⚡ **Edge Interceptor** (`core/edge/interceptor.py`)
- **mitmproxy Integration** : Hook personnalisés pour traitement avancé
- **Heuristiques d'Extraction** : Pattern matching pour données sensibles
- **Bridge Networking** : Connectivité cross-réseaux transparente
- **Performance Optimized** : Traitement asynchrone haute performance

### 🎨 **Social Templates Engine** (`core/social/templates.py`)
- **High-Fidelity Rendering** : Reproduction pixel-perfect des cibles
- **Context-Aware** : Adaptation dynamique au contexte utilisateur
- **Template Catalog** : Système de gestion centralisé des templates
- **Customization API** : Génération programmatique de templates

## Flux Principal
1. /v5/r/{campaign_id} → SmartRedirector
2. Antibot basique (UA/IP) → Page redirect.html (fingerprint)
3. POST fingerprint → verify_fingerprint → Destination
4. Template mode: /v5/phish/{cid}/login (form/JS vers /v5/auth/login…)
5. AiTM mode: /v5/p/{sid}/… → AiTMProxy réécrit et capture

## Données
- Sessions: data/sessions.json (local) + export via /v5/session/{sid}/export
- Templates: core/assets/templates/high_fidelity/*.html
- Logos/QR: core/assets/logos, core/assets/qr_codes

## Tests
- API + intégration: core/tests/
- Conseillé: pytest, mypy, bandit

