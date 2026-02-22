#!/bin/bash
# Vantablack Tier 2 Deployment Script
# ===================================
# This script deploys a Vantablack Redirector (Tier 2) on a fresh Linux server.
# It installs Nginx, configures it as a reverse proxy to the Core (Tier 3),
# and sets up basic security.

set -e

# --- Configuration ---
CORE_HOST=""
CORE_PORT="8000"
NGINX_CONF="/etc/nginx/nginx.conf"
REDIRECTOR_CONF="infrastructure/nginx/redirector.conf"

# --- Colors ---
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}>>> Vantablack Tier 2 Deployment <<<${NC}"

# --- Check Root ---
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}[!] Please run as root${NC}"
  exit 1
fi

# --- Inputs ---
read -p "Enter Vantablack Core IP/Hostname (Tier 3): " CORE_HOST
if [ -z "$CORE_HOST" ]; then
    echo -e "${RED}[!] Core Host is required${NC}"
    exit 1
fi

read -p "Enter Core Port [8000]: " input_port
CORE_PORT=${input_port:-8000}

# --- Install Nginx ---
echo -e "${GREEN}[*] Installing Nginx...${NC}"
if [ -f /etc/debian_version ]; then
    apt-get update -qq
    apt-get install -y nginx curl certbot python3-certbot-nginx
elif [ -f /etc/redhat-release ]; then
    yum install -y epel-release
    yum install -y nginx curl certbot python3-certbot-nginx
else
    echo -e "${RED}[!] Unsupported OS. Please install Nginx manually.${NC}"
    exit 1
fi

# --- Configure Nginx ---
echo -e "${GREEN}[*] Configuring Redirector...${NC}"
if [ ! -f "$REDIRECTOR_CONF" ]; then
    echo -e "${RED}[!] Configuration file $REDIRECTOR_CONF not found! Run from project root.${NC}"
    # Fallback: create minimal config inline if file missing
    cat > nginx.conf <<EOF
user www-data;
worker_processes auto;
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    upstream core { server $CORE_HOST:$CORE_PORT; }
    server {
        listen 80;
        location / {
            proxy_pass http://core;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
}
EOF
    cp nginx.conf $NGINX_CONF
    rm nginx.conf
else
    # Replace placeholders and copy
    sed "s/CORE_HOST/$CORE_HOST/g" $REDIRECTOR_CONF | sed "s/CORE_PORT/$CORE_PORT/g" > temp_nginx.conf
    mv temp_nginx.conf $NGINX_CONF
fi

# --- Test & Reload ---
echo -e "${GREEN}[*] Testing Configuration...${NC}"
nginx -t

echo -e "${GREEN}[*] Reloading Nginx...${NC}"
systemctl enable nginx
systemctl restart nginx

# --- SSL Setup (Optional) ---
read -p "Do you want to setup SSL via Certbot (Let's Encrypt)? [y/N]: " setup_ssl
if [[ "$setup_ssl" =~ ^[Yy]$ ]]; then
    read -p "Enter Domain Name (e.g., login.microsoft-security.com): " domain_name
    if [ ! -z "$domain_name" ]; then
        certbot --nginx -d $domain_name --non-interactive --agree-tos -m admin@$domain_name --redirect
    fi
fi

echo -e "${GREEN}[SUCCESS] Tier 2 Redirector Deployed!${NC}"
echo -e "Traffic -> This Server -> $CORE_HOST:$CORE_PORT"
