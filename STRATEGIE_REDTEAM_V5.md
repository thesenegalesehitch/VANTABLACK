# 🏴 STRATÉGIE OPÉRATIONNELLE RED TEAM - VANTABLACK v5

> **CLASSIFICATION**: RED TEAM EYES ONLY  
> **OBJECTIF**: DOMINATION TOTALE & INVISIBILITÉ  
> **VERSION**: 5.0 (Active Development)
> **MISSION**: Déploiement d'une infrastructure offensive résiliente, scalable et furtive pour opérations à grande échelle.

---

## 1. PHILOSOPHIE : "ASSUME DETECTION"

Nous partons du principe que la cible dispose d'EDR, de SOC, et d'analyseurs de trafic. L'outil ne doit pas seulement "fonctionner", il doit **survivre**.

### Les 3 Piliers de Vantablack v5
1.  **Invisibilité (Stealth)** : Le trafic malveillant doit être indiscernable du trafic légitime. Utilisation de "Phantasm" pour le rendu client.
2.  **Fiabilité (Reliability)** : Si l'utilisateur clique, la page DOIT s'afficher. Zéro erreur 500. Architecture asynchrone.
3.  **Persistance (Persistence)** : Si un nœud tombe, un autre prend le relais. Infrastructure "Tiered".

---

## 2. ARCHITECTURE D'INFRASTRUCTURE "TIERED" (EN COUCHES)

Pour une attaque à grande échelle, nous ne pouvons pas exposer notre serveur principal (Le C2 / Core). Nous utilisons une architecture en cascade.

```mermaid
graph TD
    User((Cible)) -->|HTTPS| Cloudflare[Tier 1: CDN / Cloudflare / Fronting]
    Cloudflare -->|Filtrage| Redirector[Tier 2: Nginx Redirectors / Dumb Proxies]
    Redirector -->|Tunnel| Core[Tier 3: Vantablack Core (Caché)]
    
    Bot((Scanner/Bot)) -->|HTTPS| Cloudflare
    Cloudflare -->|Block| Blackhole[Trous Noir / Page Légitime]
```

*   **Tier 1 (Fronting)** : Domaines jetables, CDN (Cloudflare, Azure CDN). Ils portent le certificat SSL valide.
*   **Tier 2 (Redirectors)** : Serveurs "idiots" (Nginx/Apache) qui ne font que relayer le trafic propre vers le Core et renvoyer le trafic sale (bots) vers google.com. Configuration Nginx prête (`infrastructure/nginx/redirector.conf`).
*   **Tier 3 (Core)** : Notre serveur Vantablack Dockerisé, caché derrière un VPN ou un tunnel, hébergeant la logique AiTM et le gestionnaire de campagnes.

---

## 3. COMPOSANTS CŒUR (CORE COMPONENTS)

### A. Le Moteur "Phantasm" (Client-Side Rendering)
*   **Statut**: ✅ Opérationnel (`core/assets/js/phantasm.js`)
*   **Fonction**: Moteur JavaScript universel injecté dans les templates haute fidélité. Il gère l'interactivité, la validation des champs, et la redirection fluide vers les étapes suivantes (Login -> Password -> 2FA).
*   **Avantage**: Rend le phishing indiscernable du site réel pour l'utilisateur, tout en facilitant la maintenance (un seul moteur JS pour tous les templates).
*   **Support**: Google, Microsoft, Amazon, etc. (15 templates générés).

### B. Social Engineering Manager (Campagnes)
*   **Statut**: ✅ Opérationnel (`core/social/manager.py`)
*   **Fonction**: Orchestration des campagnes.
    *   **QR Codes Polymorphes**: Génération robuste avec logos intégrés (verifié).
    *   **Gestion des Sessions**: Suivi Redis des clics et des scans.
    *   **Injection Dynamique**: `sessionId` et `campaignId` dans les templates.
*   **Flux**: Création Campagne -> Génération URL/QR -> Déploiement.

### C. Smart Redirection & Fingerprinting
*   **Statut**: ✅ Opérationnel (`core/redirect/fingerprint.py`, `core/assets/js/fingerprint_collector.js`)
*   **Fonction**: Qualification de la cible avant affichage.
    *   **Fingerprinting Avancé**: Canvas, WebGL, AudioContext, Font Detection, User-Agent.
    *   **Anti-Bot Caching**: Redis pour réduire la latence des vérifications (IP Datacenter, UA).
    *   **Geo-Fencing**: Blocage des IP hors zone cible.

### D. Le Module AiTM (Adversary-in-the-Middle)
*   **Statut**: 🚧 En cours de finalisation (`core/proxy/aitm.py`)
*   **Fonction**: Proxy inverse transparent pour capturer les sessions.
    *   **WebSockets**: Support bi-directionnel pour le trafic temps réel (MFA).
    *   **Capture**: Vol de cookie de session (SAML/OIDC) après le MFA.
    *   **Technique**: Réécriture des URLs et des réponses HTTP à la volée.

---

## 4. FLUX D'ATTAQUE (ATTACK FLOW)

1.  **Distribution**: La cible reçoit un email/SMS avec un lien ou scanne un **QR Code** généré par le Social Manager.
2.  **Filtrage (Tier 2)**: Le Redirecteur reçoit la requête. Si IP = Bot -> Redirection Google. Sinon -> Proxy vers Core.
3.  **Fingerprinting**: Le Core sert une page de chargement (`redirect.html`) qui exécute le JS de fingerprinting.
4.  **Qualification**: Les données du navigateur sont analysées. Si humain -> Redirection vers le Template de Phishing.
5.  **Phishing (Phantasm)**: La cible voit la page de login (ex: Microsoft). Elle entre son email.
    *   Phantasm envoie l'email au Core.
    *   Le Core initie la session AiTM avec le vrai serveur Microsoft.
6.  **Capture**: La cible entre son mot de passe et son code MFA.
    *   Le Core relaie au vrai serveur.
    *   Le vrai serveur renvoie le Cookie de Session.
    *   **Vantablack vole le cookie**.
7.  **Finalisation**: La cible est redirigée vers le vrai site (ou une page d'erreur crédible).

---

## 5. FEUILLE DE ROUTE (ROADMAP)

### ✅ PHASE 1 : FONDATIONS (Terminé)
*   [x] **Templates Haute Fidélité** : 15 templates majeurs (GAFAM + autres) générés.
*   [x] **Moteur Phantasm** : Logique client unifiée.
*   [x] **Gestionnaire de Campagnes** : API, Redis, QR Codes.
*   [x] **Structure du Projet** : Clean Architecture en Python/FastAPI.

### 🚧 PHASE 2 : INTELLIGENCE & PROXY (Terminé)
*   [x] **Finalisation AiTM** : Gestion robuste des websockets et du streaming.
*   [x] **Fingerprinting Avancé** : Détection des sandboxs de sécurité (Audio/Font).
*   [x] **Tiered Infrastructure** : Scripts de déploiement automatique pour les Redirecteurs Nginx.
*   [x] **Export Session** : Endpoint API pour exporter les cookies en JSON/Netscape.
*   [x] **Validation Flux** : Test de bout en bout (Campagne -> Redirect -> AiTM).
*   [x] **Landing Pages** : Template "Teams Meeting" haute fidélité créé.

### 📅 PHASE 3 : OPÉRATIONS (En cours)
*   [x] **Exfiltration Auto** : Hooks vers Telegram/Discord pour les cookies volés (`core/exfiltration`).
*   [ ] **Dashboard C2** : Interface Web pour le suivi temps réel (Matrix-style).
*   [ ] **Tests de Charge** : Valider 10k requêtes/seconde.

---

## 6. INDICATEURS DE SUCCÈS (KPI)

*   **Taux de Bypass MFA** : > 90%
*   **Détection par Chrome/SmartScreen** : < 5% après 24h
*   **Temps de déploiement** : < 5 minutes
*   **Fiabilité** : 99.9% Uptime

---

**CONCLUSION** : Vantablack v5 n'est pas un simple outil de phishing, c'est une plateforme d'ingénierie sociale de précision. La Phase 1 est achevée. Focus immédiat sur la Phase 2 (AiTM & Fingerprinting).
