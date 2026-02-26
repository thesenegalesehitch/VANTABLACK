#!/bin/bash
#
# Vantablack - Automated Redirector Deployment Script
# ==================================================
# This script generates an Nginx configuration for a Tier 2 redirector.

set -e

# --- Configuration ---
NGINX_CONFIG_PATH="/etc/nginx/sites-available/redirector.conf"
NGINX_SYMLINK_PATH="/etc/nginx/sites-enabled/redirector.conf"

# --- Functions ---
print_usage() {
    echo "Usage: $0 --domain <your_domain> --upstream-ip <c2_server_ip>"
    echo "  --domain: The domain name for the redirector (e.g., phishing.com)."
    echo "  --upstream-ip: The IP address of the Vantablack C2 server."
}

generate_nginx_config() {
    local domain=$1
    local upstream_ip=$2

    cat << EOF
server {
    listen 80;
    server_name $domain;

    # Redirect all HTTP traffic to HTTPS
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $domain;

    # SSL Configuration (to be filled by Certbot)
    # ssl_certificate /etc/letsencrypt/live/$domain/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$domain/privkey.pem;
    # include /etc/letsencrypt/options-ssl-nginx.conf;
    # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://$upstream_ip:8443; # Assuming Vantablack runs on 8443
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket Support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
}

# --- Main Logic ---
if [ "$#" -ne 4 ]; then
    print_usage
    exit 1
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --domain) DOMAIN="$2"; shift ;;
        --upstream-ip) UPSTREAM_IP="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; print_usage; exit 1 ;;
    esac
    shift
done

if [ -z "$DOMAIN" ] || [ -z "$UPSTREAM_IP" ]; then
    echo "Error: Both --domain and --upstream-ip are required."
    print_usage
    exit 1
fi

echo "[+] Generating Nginx configuration for domain: $DOMAIN"
CONFIG_CONTENT=$(generate_nginx_config "$DOMAIN" "$UPSTREAM_IP")

echo "[+] Writing configuration to temporary file..."
TMP_CONFIG_FILE=$(mktemp)
echo "$CONFIG_CONTENT" > "$TMP_CONFIG_FILE"

echo "[+] Validating generated Nginx configuration..."
nginx -t -c "$TMP_CONFIG_FILE"

echo "[+] Configuration is valid. You can now copy it to your Nginx server."
echo "    sudo cp $TMP_CONFIG_FILE $NGINX_CONFIG_PATH"
echo "    sudo ln -s $NGINX_CONFIG_PATH $NGINX_SYMLINK_PATH"
echo "    sudo systemctl restart nginx"
echo ""
echo "[+] Don't forget to obtain an SSL certificate for your domain:"
echo "    sudo certbot --nginx -d $DOMAIN"
echo ""
echo "[+] Temporary config file is at: $TMP_CONFIG_FILE"

