# Vantablack Core v5 — Red Team Operations Suite (Clean Edition)

Vantablack Core v5 is a modular, research‑oriented framework for red‑team training and security experimentation. This "Clean" edition focuses on safe, lawful use with built‑in safeguards, local self‑audit flows, and clear guidance to prevent misuse.

> Important: Use only in environments you own or explicitly control, with proper authorization. The maintainers do not condone, encourage, or support illegal activity.

## 🚀 NOUVELLES FONCTIONNALITÉS (v5.1)

### 🌍 **Tous les Réseaux Sociaux Mondiaux**
- ✅ **WhatsApp, Telegram, Snapchat, Twitch**
- ✅ **WeChat, LINE, VKontakte (VK), Spotify**
- ✅ **Facebook, Instagram, Twitter/X, Google**
- ✅ **Microsoft, LinkedIn, Amazon, Apple**
- ✅ **Discord, Dropbox, GitHub, PayPal**
- ✅ **Reddit, Slack, TikTok, Yahoo**

### 🎯 **Système de Monitoring Temps Réel**
- 🔍 **Affichage instantané** des captures dans le terminal
- 👤 **Détection OS** (Windows, macOS, Linux, Android, iOS)
- 🌐 **Analyse navigateur** (Chrome, Firefox, Safari, Edge)
- 📍 **Géolocalisation** et détection VPN
- 💡 **Instructions d'utilisation** pour chaque capture

### 🎁 **Générateur de Pages Personnalisées**
- 🎯 **Pages Giveaway** avec comptes à rebours
- 🔐 **Pages Login** professionnelles indiscernables
- 🎨 **Templates automatiques** pour campagnes
- 🚀 **Génération de phishlets** associés

### ⚡ **Installation Automatique**
- 🤖 **Détection OS** automatique (macOS, Linux, Windows)
- 📦 **Installation dépendances** système et Python
- 🐍 **Environnement virtuel** auto-configuré
- 🧪 **Tests de validation** complets

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

### Menu Interactif Complet :
```bash
python setup.py
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

### Lancer une Attaque Ciblée :
```bash
# Serveur phishing simple
python phishing_server.py --target google --port 8080

# Avec furtivité avancée
python phishing_server.py --target microsoft --stealth --lang fr

# Giveaway personnalisé
python generator.py → Option 1
```

### Génération QR Codes (Quishing) :
```bash
python quishing.py --url https://votre-lure.trycloudflare.com/login --logo google.png
```

## 🔍 Fonctionnalités de Détection

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

## 📞 Support

Pour toute question sur l'utilisation légale et éthique, consultez votre département juridique avant toute utilisation.

---

**⚠️ AVERTISSEMENT IMPORTANT** : Ce projet est destiné uniquement à la recherche légitime, la formation à la sécurité et les tests d'intrusion autorisés. Toute utilisation malveillante est strictement interdite.

**By using this software, you agree to use it only for lawful purposes and with proper authorization.**