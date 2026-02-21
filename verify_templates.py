#!/usr/bin/env python3
"""
Vérification de la génération de templates pour toutes les plateformes supportées
(Red Team Validation Script)
"""
import sys
import os
from templates.generator import TemplateGenerator, TemplateConfig

def test_platform_templates():
    platforms = [
        "google", 
        "microsoft", 
        "linkedin", 
        "facebook",
        "twitter"
    ]
    
    generator = TemplateGenerator()
    results = []
    
    print("=== DÉBUT VALIDATION TEMPLATES ===")
    
    for platform in platforms:
        print(f"\n[*] Génération template pour: {platform.upper()}")
        try:
            config = TemplateConfig(
                target_platform=platform,
                template_type="login",
                personalization_level="high",
                responsive=True,
                optimization_level="maximum",
                compliance_checks=["basic"],
                custom_variables={
                    "headline": f"Connexion {platform.title()}",
                    "subtitle": "Accès sécurisé Red Team"
                }
            )
            
            tmpl = generator.generate_template(config)
            
            filename = f"output/templates/{platform}_login.html"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(tmpl.html_content)
                
            print(f"[SUCCESS] Template généré: {filename}")
            print(f"  ID: {tmpl.template_id}")
            print(f"  Score Performance: {tmpl.performance_score}")
            results.append((platform, True))
            
        except Exception as e:
            print(f"[ERROR] Échec génération {platform}: {str(e)}")
            results.append((platform, False))
            
    print("\n=== RAPPORT FINAL ===")
    success_count = sum(1 for _, s in results if s)
    print(f"Total: {len(platforms)}")
    print(f"Succès: {success_count}")
    print(f"Échecs: {len(platforms) - success_count}")
    
    if success_count == len(platforms):
        print("\n[OK] Tous les templates sont valides pour le déploiement.")
        sys.exit(0)
    else:
        print("\n[FAIL] Certains templates ont échoué.")
        sys.exit(1)

if __name__ == "__main__":
    test_platform_templates()
