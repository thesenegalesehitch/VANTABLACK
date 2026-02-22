#!/bin/bash
# Vantablack Redirector Setup Script (Tier 2)
# Usage: ./setup.sh <DOMAIN_NAME> <CORE_IP>

set -e

DOMAIN=$1
CORE_IP=$2

if [ -z "$DOMAIN" ] || [ -z "$CORE_IP" ]; then
    echo "Usage: $0 <DOMAIN_NAME> <CORE_IP>"
    exit 1
fi

echo "[*] Vantablack Redirector Setup for $DOMAIN -> Core: $CORE_IP"

# 1. Update & Install Dependencies
echo "[*] Installing dependencies..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx ufw fail2ban curl gnupg2 ca-certificates lsb-release

# 2. Configure Firewall (UFW)
echo "[*] Configuring Firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# 3. Configure Nginx
echo "[*] Configuring Nginx..."
cat > /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl; # http2 supprimé pour compatibilité certbot initiale
    server_name $DOMAIN;

    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    server_tokens off;

    # Bot Blocking (Basic)
    if (\$http_user_agent ~* (Googlebot|Bingbot|Slurp|DuckDuckBot|Baiduspider|YandexBot|Sogou|Exabot|facebot|facebookexternalhit|ia_archiver|curl|wget|python-requests|libwww-perl|urllib|Scrapy|Nmap|Zgrab|Masscan|Go-http-client|censys|shodan|virustotal|PhishTank)) {
        return 404;
    }

    location / {
        proxy_pass http://$CORE_IP:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Hide Core Headers
        proxy_hide_header Server;
        proxy_hide_header X-Powered-By;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 4. SSL Certificate (Let's Encrypt)
echo "[*] Obtaining SSL Certificate..."
# Stop Nginx for standalone challenge if needed, but we use nginx plugin
service nginx reload
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN --redirect

# 5. Fail2Ban Configuration (Optional but recommended)
echo "[*] Configuring Fail2Ban..."
cat > /etc/fail2ban/jail.d/nginx-botsearch.conf <<EOF
[nginx-botsearch]
enabled = true
port = http,https
filter = nginx-botsearch
logpath = /var/log/nginx/error.log
maxretry = 2
EOF
service fail2ban restart

echo "[SUCCESS] Redirector $DOMAIN is ready!"
echo "Make sure your Core server ($CORE_IP) allows traffic from this IP."
