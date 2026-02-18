#!/usr/bin/env bash
set -uo pipefail
DOMAIN="${1:-x.local}"
KC_SYS="/Library/Keychains/System.keychain"
KC_USER="$HOME/Library/Keychains/login.keychain-db"
if grep -q "[[:space:]]$DOMAIN$" /etc/hosts; then
  if sudo sed -i '' "/[[:space:]]$DOMAIN$/d" /etc/hosts; then
    echo "[OK] /etc/hosts nettoyé pour $DOMAIN"
  else
    echo "[WARN] Impossible de modifier /etc/hosts. Supprime manuellement la ligne pour $DOMAIN"
  fi
else
  echo "[OK] Aucun host $DOMAIN dans /etc/hosts"
fi
for KC in "$KC_SYS" "$KC_USER"; do
  if [ -f "$KC" ]; then
    SHA_LIST=$(security find-certificate -a -Z -c mitmproxy -k "$KC" 2>/dev/null | awk '/SHA-1 hash:/ {print $3}')
    if [ -n "$SHA_LIST" ]; then
      for Z in $SHA_LIST; do
        if security delete-certificate -Z "$Z" -k "$KC" >/dev/null 2>&1; then
          echo "[OK] Cert mitmproxy supprimé ($Z) de $KC"
        fi
      done
    else
      echo "[OK] Aucun cert mitmproxy trouvé dans $KC"
    fi
  fi
done
echo "[OK] Désinstallation terminée"
