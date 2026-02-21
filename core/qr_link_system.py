"""
Vantablack QR & Link System v2.0
================================

Système robuste de génération, validation et fusion QR/liens avec :
- Validation multi-OS complète
- Métriques de performance
- Gestion d'erreurs professionnelle
- Support SSL/TLS complet
- Customisation avancée
"""

import os
import sys
import platform
import subprocess
import requests
import socket
import ssl
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum
import json
import logging

from PIL import Image
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QRCorrectionLevel(Enum):
    """Niveaux de correction d'erreur QR"""
    LOW = ERROR_CORRECT_L
    MEDIUM = ERROR_CORRECT_M
    QUALITY = ERROR_CORRECT_Q
    HIGH = ERROR_CORRECT_H


class LinkValidationResult(Enum):
    """Résultats de validation de lien"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    SSL_ERROR = "ssl_error"
    NETWORK_ERROR = "network_error"
    INVALID_URL = "invalid_url"
    LOCALHOST_ONLY = "localhost_only"


@dataclass
class ValidationMetrics:
    """Métriques de validation"""
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    average_response_time: float = 0.0
    ssl_errors: int = 0
    network_errors: int = 0


@dataclass
class QRConfig:
    """Configuration de génération QR"""
    version: int = 1
    error_correction: QRCorrectionLevel = QRCorrectionLevel.HIGH
    box_size: int = 10
    border: int = 4
    fill_color: str = "black"
    back_color: str = "white"
    logo_path: Optional[str] = None
    logo_scale_factor: int = 4


class QRLinkSystem:
    """Système complet de gestion QR/liens"""
    
    def __init__(self):
        self.metrics = ValidationMetrics()
        self._setup_os_specific_checks()
    
    def _setup_os_specific_checks(self):
        """Configuration des vérifications spécifiques à l'OS"""
        self.os_type = platform.system()
        self.install_commands = self._get_install_commands()
    
    def _get_install_commands(self) -> Dict[str, str]:
        """Retourne les commandes d'installation par OS"""
        return {
            "Darwin": "brew install zbar && pip install 'qrcode[pil]' pyzbar",
            "Linux": "sudo apt-get install -y libzbar0 && pip install 'qrcode[pil]' pyzbar",
            "Windows": "pip install 'qrcode[pil]' pyzbar"
        }
    
    def validate_url(self, url: str, timeout: float = 5.0) -> Tuple[bool, LinkValidationResult, Dict]:
        """
        Validation robuste d'une URL avec support SSL/TLS complet
        """
        self.metrics.total_checks += 1
        
        # Validation syntaxique de l'URL
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                self.metrics.failed_checks += 1
                return False, LinkValidationResult.INVALID_URL, {"error": "URL syntaxiquement invalide"}
        except Exception:
            self.metrics.failed_checks += 1
            return False, LinkValidationResult.INVALID_URL, {"error": "URL syntaxiquement invalide"}
        
        # Vérification localhost vs distant
        is_local = parsed.hostname in ['localhost', '127.0.0.1', '::1']
        
        start_time = time.time()
        
        try:
            # Configuration de la requête avec timeout et vérification SSL
            session = requests.Session()
            session.verify = True  # Validation SSL activée
            
            response = session.get(url, timeout=timeout, allow_redirects=True)
            response_time = time.time() - start_time
            
            # Mise à jour des métriques
            self.metrics.successful_checks += 1
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.successful_checks - 1) + response_time) 
                / self.metrics.successful_checks
            )
            
            return True, LinkValidationResult.SUCCESS, {
                "status_code": response.status_code,
                "response_time": response_time,
                "is_local": is_local,
                "ssl_valid": response.url.startswith('https')
            }
            
        except requests.exceptions.SSLError as e:
            self.metrics.failed_checks += 1
            self.metrics.ssl_errors += 1
            return False, LinkValidationResult.SSL_ERROR, {"error": str(e)}
            
        except requests.exceptions.Timeout:
            self.metrics.failed_checks += 1
            return False, LinkValidationResult.TIMEOUT, {"error": "Timeout"}
            
        except requests.exceptions.ConnectionError as e:
            self.metrics.failed_checks += 1
            self.metrics.network_errors += 1
            
            # Vérification spécifique pour les erreurs de connexion
            if "Connection refused" in str(e) and is_local:
                return False, LinkValidationResult.LOCALHOST_ONLY, {"error": "Service local non démarré"}
            
            return False, LinkValidationResult.NETWORK_ERROR, {"error": str(e)}
            
        except Exception as e:
            self.metrics.failed_checks += 1
            return False, LinkValidationResult.NETWORK_ERROR, {"error": str(e)}
    
    def generate_qr(self, data: str, output_path: str, config: Optional[QRConfig] = None) -> Tuple[bool, str]:
        """
        Génération robuste de QR code avec gestion d'erreurs complète
        """
        if config is None:
            config = QRConfig()
        
        try:
            # Création du QR code
            qr = qrcode.QRCode(
                version=config.version,
                error_correction=config.error_correction.value,
                box_size=config.box_size,
                border=config.border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Génération de l'image
            img = qr.make_image(
                fill_color=config.fill_color,
                back_color=config.back_color
            ).convert('RGB')
            
            # Ajout du logo si spécifié
            if config.logo_path and os.path.exists(config.logo_path):
                success, message = self._add_logo_to_qr(img, config.logo_path, config.logo_scale_factor)
                if not success:
                    logger.warning(f"Échec ajout logo: {message}")
            
            # Sauvegarde de l'image
            img.save(output_path)
            logger.info(f"QR généré avec succès: {output_path}")
            return True, "QR généré avec succès"
            
        except ImportError as e:
            error_msg = f"Dépendances manquantes: {e}. Installer: {self.install_commands.get(self.os_type, 'pip install qrcode[pil]')}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Erreur génération QR: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _add_logo_to_qr(self, qr_image: Image.Image, logo_path: str, scale_factor: int = 4) -> Tuple[bool, str]:
        """Ajoute un logo au centre du QR code"""
        try:
            logo = Image.open(logo_path)
            
            # Redimensionnement du logo
            img_w, img_h = qr_image.size
            logo_w = int(img_w / scale_factor)
            logo_h = int(img_h / scale_factor)
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            
            # Positionnement au centre
            pos_x = (img_w - logo_w) // 2
            pos_y = (img_h - logo_h) // 2
            
            # Collage du logo (avec support transparence)
            if logo.mode == 'RGBA':
                qr_image.paste(logo, (pos_x, pos_y), logo)
            else:
                qr_image.paste(logo, (pos_x, pos_y))
            
            return True, "Logo ajouté avec succès"
            
        except Exception as e:
            return False, f"Erreur ajout logo: {e}"
    
    def decode_qr(self, image_path: str) -> Tuple[bool, List[str]]:
        """Décodage de QR code avec support multi-OS"""
        try:
            from pyzbar.pyzbar import decode
            
            img = Image.open(image_path)
            results = decode(img)
            
            if not results:
                return False, ["Aucune donnée QR détectée"]
            
            decoded_data = []
            for result in results:
                try:
                    data = result.data.decode('utf-8', errors='ignore')
                    decoded_data.append(data)
                except Exception as e:
                    decoded_data.append(f"[Données binaires: {len(result.data)} bytes]")
            
            return True, decoded_data
            
        except ImportError:
            error_msg = f"Bibliothèque de décodage manquante. Installer: {self.install_commands.get(self.os_type, 'pip install pyzbar')}"
            return False, [error_msg]
            
        except Exception as e:
            return False, [f"Erreur décodage: {e}"]
    
    def generate_qr_with_link_validation(self, url: str, output_path: str, 
                                        validate: bool = True, 
                                        config: Optional[QRConfig] = None) -> Dict:
        """
        Génération de QR avec validation automatique du lien
        """
        result = {
            "qr_generated": False,
            "link_valid": False,
            "validation_result": None,
            "error": None,
            "metrics": self.metrics.__dict__
        }
        
        # Validation du lien si demandé
        if validate:
            is_valid, validation_result, details = self.validate_url(url)
            result["link_valid"] = is_valid
            result["validation_result"] = validation_result.value
            result["validation_details"] = details
            
            if not is_valid and validation_result == LinkValidationResult.LOCALHOST_ONLY:
                logger.warning("Service local non démarré - Génération QR quand même")
            elif not is_valid:
                result["error"] = f"Lien invalide: {validation_result.value}"
                return result
        
        # Génération du QR
        success, message = self.generate_qr(url, output_path, config)
        result["qr_generated"] = success
        
        if not success:
            result["error"] = message
        
        return result
    
    def get_installation_guide(self) -> str:
        """Retourne le guide d'installation pour l'OS courant"""
        return self.install_commands.get(self.os_type, "pip install 'qrcode[pil]' pyzbar")
    
    def get_metrics(self) -> Dict:
        """Retourne les métriques de performance"""
        return self.metrics.__dict__


# Instance globale pour une utilisation facile
qr_link_system = QRLinkSystem()


def test_qr_system():
    """Fonction de test du système QR/liens"""
    system = QRLinkSystem()
    
    # Test de validation
    test_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404", 
        "http://localhost:9999/",  # Devrait échouer (service local)
        "https://invalid-domain-that-does-not-exist-12345.com"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Validation: {url}")
        is_valid, result, details = system.validate_url(url, timeout=3)
        print(f"   Résultat: {result.value}")
        print(f"   Détails: {details}")
    
    # Test génération QR
    print(f"\n📊 Métriques: {system.get_metrics()}")


if __name__ == "__main__":
    test_qr_system()