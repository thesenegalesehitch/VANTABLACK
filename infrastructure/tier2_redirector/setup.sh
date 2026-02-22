
#!/bin/bash

# Tier 2 Redirector Setup Script
# Usage: ./setup.sh <DOMAIN> <CORE_IP>

DOMAIN=$1
CORE_IP=$2

if [ -z "$DOMAIN" ] || [ -z "$CORE_IP" ]; then
    echo "Usage: ./setup.sh <DOMAIN> <CORE_IP>"
    exit 1
fi

echo "[*] Setting up Tier 2 Redirector for $DOMAIN -> $CORE_IP"

# 1. Install Dependencies
echo "[*] Updating system and installing Nginx..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx ufw

# 2. Firewall Setup
echo "[*] Configuring Firewall..."
ufw allow 'Nginx Full'
ufw allow ssh
ufw --force enable

# 3. SSL Certificate (Certbot)
echo "[*] Obtaining SSL Certificate..."
# Using --standalone temporarily to get cert, then Nginx will manage it
systemctl stop nginx
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 4. Configure Nginx
echo "[*] Configuring Nginx..."
TEMPLATE_PATH="./nginx.conf"
DEST_PATH="/etc/nginx/nginx.conf"

if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "[!] Template nginx.conf not found! Downloading default or aborting."
    # Ideally download from repo, here we assume it's present
    exit 1
fi

cp $TEMPLATE_PATH $DEST_PATH

# Replace Placeholders
sed -i "s/{{DOMAIN}}/$DOMAIN/g" $DEST_PATH
sed -i "s/{{CORE_IP}}/$CORE_IP/g" $DEST_PATH

# 5. Start Nginx
echo "[*] Starting Nginx..."
systemctl start nginx
systemctl enable nginx

# 6. Verify
nginx -t
if [ $? -eq 0 ]; then
    echo "[+] Redirector Setup Complete! Traffic will flow to $CORE_IP"
    systemctl restart nginx
else
    echo "[!] Nginx configuration error!"
    exit 1
fi
