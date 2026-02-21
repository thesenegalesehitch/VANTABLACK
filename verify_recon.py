#!/usr/bin/env python3
"""
Vérification des capacités de reconnaissance pour toutes les plateformes
(Red Team Validation Script)
"""
import sys
from core.recon.analyzer import get_recon_module

def test_recon_capabilities():
    targets = [
        ("@pseudo_x", "twitter"),
        ("user@gmail.com", "google"),
        ("pro@linkedin.com", "linkedin"),
        ("user@outlook.com", "microsoft"),
        ("id_facebook", "facebook")
    ]
    
    print("=== DÉBUT VALIDATION RECONNAISSANCE ===")
    
    success = True
    
    for target, platform in targets:
        print(f"\n[*] Analyse cible: {target} ({platform})")
        try:
            recon = get_recon_module(platform, target)
            data = recon.analyze()
            
            # Validation des champs clés
            required_fields = ["target", "platform", "profile_found", "recommended_phishlet"]
            missing = [f for f in required_fields if f not in data]
            
            if missing:
                print(f"[FAIL] Champs manquants: {missing}")
                success = False
            else:
                print(f"[SUCCESS] Données récupérées: {len(data)} champs")
                print(f"  Score Sécurité: {data.get('security_score')}")
                print(f"  Phishlet Recommandé: {data.get('recommended_phishlet')}")
                
        except Exception as e:
            print(f"[ERROR] Échec analyse {platform}: {str(e)}")
            success = False
            
    if success:
        print("\n[OK] Module de reconnaissance opérationnel pour toutes les cibles.")
        sys.exit(0)
    else:
        print("\n[FAIL] Certains tests de reconnaissance ont échoué.")
        sys.exit(1)

if __name__ == "__main__":
    test_recon_capabilities()
