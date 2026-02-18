#!/usr/bin/env bash
set -euo pipefail
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
  echo "127.0.0.1 $DOMAIN" | sudo tee -a /etc/hosts >/dev/null
fi
if ! sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$CA"; then
  security add-trusted-cert -d -r trustRoot -k "$HOME/Library/Keychains/login.keychain-db" "$CA"
fi
open "https://$DOMAIN:$PORT/i/flow/login" >/dev/null 2>&1 || true
