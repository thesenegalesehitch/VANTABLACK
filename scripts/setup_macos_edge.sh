#!/usr/bin/env bash
set -uo pipefail
DOMAIN="${1:-x.local}"
PORT="${2:-8443}"
CA="$HOME/.mitmproxy/mitmproxy-ca-cert.pem"
if [ ! -f "$CA" ]; then
  if command -v mitmproxy >/dev/null 2>&1; then
    mitmproxy --set console_eventlog_verbosity=error --listen-port 65535 --quit >/dev/null 2>&1 || true
  else
    echo "mitmproxy non installé. Installe: python -m pip install mitmproxy"
    exit 1
  fi
fi
if ! grep -q "$DOMAIN" /etc/hosts; then
  echo "Tentative d'ajout de $DOMAIN dans /etc/hosts (sudo requis)…"
  if ! echo "127.0.0.1 $DOMAIN" | sudo tee -a /etc/hosts >/dev/null; then
    echo "[WARN] Impossible d'écrire /etc/hosts sans privilèges. Ajoute manuellement:"
    echo "      echo \"127.0.0.1 $DOMAIN\" | sudo tee -a /etc/hosts"
  else
    echo "[OK] /etc/hosts mis à jour pour $DOMAIN"
  fi
fi
echo "Import de la CA mitmproxy…"
if ! sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$CA"; then
  echo "[WARN] Import système refusé. Tentative dans le Trousseau utilisateur (login)…"
  if security add-trusted-cert -d -r trustRoot -k "$HOME/Library/Keychains/login.keychain-db" "$CA"; then
    echo "[OK] CA ajoutée au Trousseau utilisateur"
  else
    echo "[ERR] Échec d'import de la CA. Ouvre Trousseaux et importe: $CA"
  fi
else
  echo "[OK] CA ajoutée au Trousseau Système"
fi
echo "Ouverture du navigateur vers https://$DOMAIN:$PORT/i/flow/login"
open "https://$DOMAIN:$PORT/i/flow/login" >/dev/null 2>&1 || true
