# 🕶️ Vantablack Core v5 — Framework Avancé de Test d'Intrusion

**Framework modulaire de recherche et de formation à la sécurité offensive** - Édition "Clean" avec protections intégrées

> ⚠️ **Avertissement Important** : Utilisation exclusive sur des environnements autorisés. Conformité légale obligatoire.

## 🚀 Capacités Techniques Avancées (v5.1+)

### 🌍 **Couverture Mondiale Complète**
- **📱 Messageries Instantanées** : WhatsApp, Telegram, Signal, LINE, WeChat
- **💼 Professionnel** : Microsoft 365, Google Workspace, LinkedIn, Slack
- **🛒 E-commerce** : Amazon, Apple ID, PayPal, eBay
- **🎮 Gaming & Streaming** : Discord, Twitch, Steam, Epic Games
- **🌐 Réseaux Sociaux** : Facebook, Instagram, Twitter/X, TikTok, Reddit
- **☁️ Cloud Storage** : Dropbox, Google Drive, OneDrive, iCloud

### 🔍 **Système de Reconnaissance Avancée**
- **🖥️ Fingerprinting Polymorphique** : Collecte complète des empreintes navigateur
- **🌐 Géolocalisation Précise** : IP, timezone, langue, résolution d'écran
- **🔧 Détection Technique** : OS, navigateur, plugins, WebGL, Canvas
- **🤖 Anti-Bot Intelligent** : Détection automatique des automates et scanners
- **📊 Analytics Temps Réel** : Dashboard live avec métriques détaillées

### 🎨 **Ingénierie Sociale Avancée**
- **📝 Templates Haute Fidélité** : Reproduction pixel-perfect des plateformes cibles
- **⚡ Génération Dynamique** : Pages adaptatives en fonction du contexte
- **🎯 Campagnes Personnalisées** : Création de scénarios ciblés spécifiques
- **🔗 Système de Redirection Intelligent** : Routage adaptatif basé sur le fingerprinting

### ⚡ **Infrastructure Professionnelle**
- **🏗️ Architecture Modulaire** : Composants indépendants et extensibles
- **🔒 Sécurité Renforcée** : Validation de type, analyse statique, sandboxing
- **🚀 Performances Optimisées** : Async/await, connexions persistantes, caching Redis
- **📦 CI/CD Intégré** : Tests automatisés, validation de qualité, déploiement
- **🐳 Containerisation** : Docker, Kubernetes, déploiement cloud-ready

## 🚀 Démarrage Ultra-Rapide

### Installation One-Click (Recommandé) :
```bash
# Installation complète automatique
python start.py
# → Choisir l'option 1
```

### Installation Manuelle :
```bash
# 1. Environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Dépendances
python -m pip install -r requirements.txt

# 3. Installation automatique
python install_deps.py
```

### Serveur UI (Dashboard)
```bash
python -m uvicorn core.web.server:create_app --reload --port 8000
# UI: http://localhost:8000/ui
```

## 📋 Plateformes Supportées

### 📱 Messageries & Réseaux Sociaux
- **WhatsApp** (`whatsapp.yaml`) - Capture numéros et codes
- **Telegram** (`telegram.yaml`) - Identifiants et codes 2FA
- **Snapchat** (`snapchat.yaml`) - Comptes Snapchat
- **Facebook/Instagram** (`facebook.yaml`, `instagram.yaml`)
- **Twitter/X** (`x.yaml`) - Login Twitter/X

### 🏢 Entreprise & Professionnel
- **Microsoft** (`microsoft.yaml`) - Office 365, Azure AD
- **Google** (`google.yaml`) - Gmail, Google Workspace
- **LinkedIn** (`linkedin.yaml`) - Réseau professionnel
- **Slack** (`slack.yaml`) - Communications d'équipe

### 🎵 Streaming & Divertissement
- **Spotify** (`spotify.yaml`) - Comptes Premium
- **Twitch** (`twitch.yaml`) - Streamers et viewers
- **Discord** (`discord.yaml`) - Communautés gaming

### 🌏 Asie & International
- **WeChat** (`wechat.yaml`) - Messagerie chinoise
- **LINE** (`line.yaml`) - Japon et Asie du Sud-Est
- **VKontakte** (`vk.yaml`) - Réseau social russe

### 💰 Finance & E-commerce
- **PayPal** (`paypal.yaml`) - Comptes de paiement
- **Amazon** (`amazon.yaml`) - Comptes shopping
- **Apple** (`apple.yaml`) - ID Apple et iCloud

## 🎯 Utilisation Avancée

### Monitoring Temps Réel :
```bash
python monitor.py
# → Option 1 pour surveillance en direct
```

### Génération de Pages Personnalisées :
```bash
python generator.py
# → Créer giveaways, pages login, campagnes
```

### Lancer un serveur de test ciblé :
```bash
# Serveur de test simple
python phishing_server.py --target google --port 8080

# Mode furtif (démo)
python phishing_server.py --target microsoft --stealth --lang fr

# Giveaway personnalisé
python generator.py → Option 1
```

### Génération QR Codes (Quishing) :
```bash
python quishing.py --url https://votre-lure.trycloudflare.com/login --logo google.png
```

## 🔍 Fonctionnalités de Détection (Recherche)

### 📊 Analyse de l'Attaquant :
- **OS Fingerprinting** : Détection précise du système
- **Browser Detection** : Navigateur et version
- **Géolocalisation** : Pays, ville, FAI depuis IP
- **VPN Detection** : Identification des connexions masquées
- **User-Agent Analysis** : Analyse complète du device

### 🎯 Capture des Données :
- ✅ **Identifiants** : Emails, usernames, mots de passe
- ✅ **Cookies** : Sessions et tokens d'authentification
- ✅ **Tokens** : OAuth, JWT, codes 2FA
- ✅ **Métadonnées** : IP, User-Agent, timestamp
- ✅ **Données personnelles** : Noms, téléphones, pays

### 💾 Stockage des Données :
- **`data/sessions.json`** : Sessions complètes avec credentials
- **`core/logs/captures.jsonl`** : Flux temps réel des captures
- **Export JSON** : Format standardisé pour analyse

## 🛡️ Sécurité et Conformité

### ✅ Mesures de Sécurité :
- Environnements virtuels isolés
- Pas de logging de secrets par défaut
- Validation automatique des configurations
- Safeguards intégrés contre les misuse

### 📜 Conformité Légale :
- Usage uniquement dans des environnements contrôlés
- Authorization explicite requise
- Research et training défensif seulement
- Audit trails complets

## 🚨 Bonnes Pratiques

1. **Toujours utiliser** dans des environnements contrôlés
2. **Authorization écrite** obligatoire
3. **Environnements isolés** sans accès internet réel
4. **Suppression des données** après usage
5. **Respect des lois** locales et internationales

## 🆘 Support et Dépannage

### Tests de Validation :
```bash
# Validation complète
python -m pytest core/tests/ -v

# Test spécifique
python -m pytest core/tests/test_fingerprint_validator.py -v
```

### Vérifications Qualité
```bash
# Type checking
mypy core/ --ignore-missing-imports

# Analyse sécurité (non bloquante)
bandit -q -r core -x core/assets,core/web/static
```

### Problèmes Courants :
- **Dépendances manquantes** : `python install_deps.py`
- **Environnement virtuel** : `python -m venv .venv`
- **Ports occupés** : Changer le port avec `--port 9090`

## 📦 Structure du Projet

```
Vantablack_Clean/
├── 📁 phishlets/          # Configuration des plateformes
├── 📁 core/               # Cœur du système
├── 📁 api/               # API REST et WebSocket
├── 📁 data/              # Données capturées
├── 📁 scripts/           # Scripts utilitaires
├── 📁 templates/         # Templates personnalisés
├── ⚡ setup.py           # Installation automatique
├── ⚡ start.py           # Démarrage rapide
├── ⚡ monitor.py         # Monitoring temps réel
├── ⚡ generator.py        # Générateur de pages
└── ⚡ install_deps.py    # Installation dépendances
```

## 📖 Documentation

- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Quickstart: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- Sécurité & usage responsable: [docs/SECURITY.md](docs/SECURITY.md)

## 📞 Support

Pour toute question sur l'utilisation légale et éthique, consultez votre département juridique avant toute utilisation.

---

**⚠️ AVERTISSEMENT IMPORTANT** : Ce projet est destiné uniquement à la recherche légitime, la formation à la sécurité et les tests d'intrusion autorisés. Toute utilisation malveillante est strictement interdite.

**By using this software, you agree to use it only for lawful purposes and with proper authorization.**
