#!/bin/bash
# Vantablack Redirector Setup Script (Tier 2)
# Usage: ./setup.sh <DOMAIN_NAME> <CORE_IP> [EMAIL]

set -e

DOMAIN=$1
CORE_IP=$2
EMAIL=${3:-"admin@$DOMAIN"}

if [ -z "$DOMAIN" ] || [ -z "$CORE_IP" ]; then
    echo "Usage: $0 <DOMAIN_NAME> <CORE_IP> [EMAIL]"
    exit 1
fi

echo "[*] Starting Vantablack Redirector Setup..."
echo "    Domain: $DOMAIN"
echo "    Core IP: $CORE_IP"
echo "    Email: $EMAIL"

# 1. Update & Install Dependencies
echo "[*] Installing dependencies (nginx, certbot, fail2ban, nginx-extras)..."
apt-get update
apt-get install -y nginx nginx-extras certbot python3-certbot-nginx ufw fail2ban curl gnupg2 ca-certificates lsb-release

# 2. Configure Firewall (UFW)
echo "[*] Configuring Firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
# If using WireGuard/VPN, allow it here too (e.g., ufw allow 51820/udp)
ufw --force enable

# 3. Configure Nginx
echo "[*] applying Nginx configuration..."

# Backup default config
mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# Create new config from template (assuming nginx.conf is in the same dir or we write it here)
# Since this script runs on the server, we'll write the content directly or download it.
# For this tool, we assume the user uploads nginx.conf to /tmp/nginx.conf or we write it now.

# We will use sed to replace placeholders in the provided nginx.conf
# Note: In a real deployment, we'd copy the file. Here we construct it dynamically or assume it's present.
# Let's assume the operator SCP'd the nginx.conf along with this script.

if [ -f "nginx.conf" ]; then
    cp nginx.conf /etc/nginx/nginx.conf
else
    echo "[!] nginx.conf not found in current directory. Downloading default or using embedded..."
    # Fallback: We write the content we defined in the IDE
    # (This part would ideally fetch from a repo)
    echo "Error: nginx.conf must be present."
    exit 1
fi

# Replace placeholders
sed -i "s/server 127.0.0.1:8000;/server $CORE_IP:8000;/g" /etc/nginx/nginx.conf
sed -i "s/server_name _;/server_name $DOMAIN;/g" /etc/nginx/nginx.conf

# 4. SSL Certificate (Let's Encrypt)
echo "[*] Obtaining SSL Certificate for $DOMAIN..."
# We use --register-unsafely-without-email if no email, but we have one.
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect

# 5. Fail2Ban Configuration
echo "[*] Configuring Fail2Ban for Nginx..."
cat > /etc/fail2ban/jail.d/nginx-botsearch.conf <<EOF
[nginx-botsearch]
enabled = true
port = http,https
filter = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 3600
findtime = 600
EOF

service fail2ban restart
service nginx restart

echo "[SUCCESS] Redirector $DOMAIN is ready!"
echo "[INFO] Traffic is proxied to $CORE_IP:8000"
echo "[INFO] Bot filtering is ACTIVE."
