# Sécurité & Usage Responsable

## Principes
- Utilisation sur environnements autorisés uniquement
- Aucune donnée sensible hors périmètre légal
- Journalisation minimale, pas de secrets en clair

## Bonnes pratiques
- Isoler l’environnement (.venv)
- Exécuter mypy/pytest/bandit avant toute livraison
- Nettoyer data/sessions.json après tests

## Réduction de surface
- Middleware Tier2 pour endpoints internes
- AntiBot basique UA/IP + fingerprint côté redirect
- CSP/CORS ajustés côté proxy et UI
