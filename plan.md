# Plan d'Attaque Red Team - Scénario Vantablack v5

Ce document détaille le scénario d'attaque complet implémenté dans Vantablack v5 pour les opérations Red Team.
**Statut: 100% Opérationnel**

## Objectif
Compromission de comptes cibles via une chaîne d'attaque sophistiquée incluant reconnaissance OSINT, weaponization de QR codes (Quishing), et exfiltration de sessions (Cookies/Tokens) sans déclencher d'alertes de sécurité.

## Phase 1 : Reconnaissance (OSINT)
**Objectif**: Identifier les cibles et personnaliser l'attaque.
**Outil**: `vanta analyze`
- **Action**: Collecte automatisée de données publiques (Twitter, LinkedIn, etc.).
- **Output**: Profil JSON enrichi (`target_profile.json`) contenant :
  - Score de sécurité estimé
  - Phishlet recommandé
  - Leurre suggéré (Security Alert vs Password Reset)
  - E-mail simulé pour le ciblage

## Phase 2 : Weaponization (Armement)
**Objectif**: Préparer l'infrastructure d'attaque.
**Outil**: `vanta edge-run` & Phishlets YAML
- **Configuration**: Chargement des phishlets optimisés (Tier 1, 2, 3).
- **Capacités**:
  - Contournement MFA via capture de tokens de session (Cookies).
  - Suppression des en-têtes de sécurité (`X-Frame-Options`, `Content-Security-Policy`).
  - Injection de scripts de tracking comportemental (`capture.js`).
- **Phishlets Prêts (100%)**:
  - **Tier 1**: Google, Microsoft (O365), LinkedIn, Facebook/Meta
  - **Tier 2**: Amazon, Apple, Github, PayPal, Dropbox
  - **Tier 3**: Discord, Reddit, Slack, TikTok, Yahoo, X (Twitter)

## Phase 3 : Distribution
**Objectif**: Délivrer la charge utile à la cible.
**Outil**: `vanta safe-qr`
- **Vecteur**: QR Code haute densité avec correction d'erreur (Level H).
- **Technique**: "Quishing" (QR Phishing) pour contourner les filtres email classiques.
- **Personnalisation**: Incrustation de logos (ex: Logo Microsoft/Google) au centre du QR pour la crédibilité.
- **Lien**: Redirection vers le proxy MitM (ex: `http://localhost:8443`).

## Phase 4 : Capture (Exploitation)
**Objectif**: Intercepter les identifiants et sessions.
**Outil**: `vanta edge-run` (Mode Proxy)
- **Mécanisme**: Proxy Inverse (MitM) transparent.
- **Données Capturées**:
  - Identifiants (Login/Password)
  - Tokens d'authentification (Session Cookies, OAuth Tokens)
  - Données comportementales (Keystrokes, Mouse movements) via `capture.js`.
- **Persistance**: Sauvegarde automatique des sessions dans `sessions.json`.

## Phase 5 : Accès (Post-Exploitation)
**Objectif**: Utiliser les sessions volées.
**Outil**: `vanta loot`
- **Action**: Exporter et visualiser les sessions capturées.
- **Utilisation**: Importation des cookies (ex: EditThisCookie) pour accéder au compte sans reconnexion (Session Replay).
- **Bypass**: Contourne le 2FA car le cookie de session est déjà authentifié.

## Phase 6 : Monitoring & Reporting
**Objectif**: Suivi en temps réel et rapport de fin de mission.
**Outil**: Beacon API & Logs
- **Télémétrie**: Envoi discret de données via `navigator.sendBeacon`.
- **Analyse**: Détection des anomalies et succès de l'attaque.
- **Rapport**: Génération de preuves de concept (PoC) pour le client.

---

## Commandes Clés

| Phase | Commande | Description |
|-------|----------|-------------|
| **1. Recon** | `vanta analyze --target @user --platform linkedin` | Analyse OSINT de la cible |
| **2. Setup** | `vanta edge-run --path phishlets/microsoft.yaml` | Lancement du proxy d'attaque |
| **3. Distrib** | `vanta safe-qr --url http://localhost:8443 --logo ...` | Génération du QR Code piégé |
| **4. Loot** | `vanta loot --export chrome` | Export des sessions capturées |

## Couverture Phishlets (100%)

Toutes les plateformes suivantes sont configurées avec règles de capture (Creds + Tokens) et bypass de sécurité :
- **Google** (Gmail/Workspace)
- **Microsoft** (Office 365/Outlook)
- **LinkedIn**
- **Facebook**
- **X (Twitter)**
- **Amazon**
- **Apple**
- **GitHub**
- **PayPal**
- **Dropbox**
- **Discord**
- **Reddit**
- **Slack**
- **TikTok**
- **Yahoo**
