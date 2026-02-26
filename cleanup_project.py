#!/usr/bin/env python3
"""
Vantablack Core v5 - Nettoyage du Projet
Supprime les fichiers obsolètes, temporaires et inutiles
"""

import os
import shutil
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ProjectCleaner:
    def __init__(self):
        self.project_root = Path(__file__).parent
        
        # Fichiers et dossiers à supprimer (obsolètes)
        self.files_to_remove = [
            # Fichiers Python obsolètes
            'old_setup.py', 'old_install.py', 'legacy_*.py',
            'test_*.py.bak', '*.pyc', '__pycache__/',
            
            # Fichiers de configuration anciens
            'config.old', 'settings.bak', 'backup_*.yaml',
            
            # Logs et temporaires
            '*.log', '*.tmp', '*.temp', 'temp/', 'tmp/',
            
            # Fichiers de développement
            'debug_*', 'dev_*', '.DS_Store', 'Thumbs.db'
        ]
        
        # Dossiers à vider mais pas supprimer
        self.dirs_to_clean = [
            'logs/', 'cache/', 'temp/', 'tmp/'
        ]
    
    def find_obsolete_files(self):
        """Trouve les fichiers obsolètes"""
        obsolete_files = []
        
        for pattern in self.files_to_remove:
            if pattern.endswith('/'):
                # C'est un dossier
                dir_pattern = pattern[:-1]
                for match in self.project_root.glob(f"**/{dir_pattern}"):
                    if match.is_dir():
                        obsolete_files.append(match)
            else:
                # C'est un pattern de fichier
                for match in self.project_root.glob(f"**/{pattern}"):
                    obsolete_files.append(match)
        
        return obsolete_files
    
    def clean_directories(self):
        """Nettoie les dossiers temporaires"""
        cleaned_dirs = []
        
        for dir_pattern in self.dirs_to_clean:
            dir_path = self.project_root / dir_pattern
            if dir_path.exists() and dir_path.is_dir():
                # Vider le dossier mais le garder
                for item in dir_path.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                cleaned_dirs.append(dir_path)
        
        return cleaned_dirs
    
    def remove_obsolete_files(self, files):
        """Supprime les fichiers obsolètes"""
        removed_files = []
        
        for file_path in files:
            try:
                if file_path.is_file():
                    file_path.unlink()  # Supprimer le fichier
                    removed_files.append(file_path)
                elif file_path.is_dir():
                    shutil.rmtree(file_path)  # Supprimer le dossier récursivement
                    removed_files.append(file_path)
            except Exception as e:
                print(f"{Colors.RED}❌ Erreur suppression {file_path}: {e}{Colors.RESET}")
        
        return removed_files
    
    def run_cleanup(self, dry_run=False):
        """Exécute le nettoyage complet"""
        print(f"{Colors.BOLD}{Colors.CYAN}=== NETTOYAGE DU PROJET VANTABLACK ==={Colors.RESET}")
        
        # Trouver les fichiers obsolètes
        obsolete_files = self.find_obsolete_files()
        
        if dry_run:
            print(f"{Colors.YELLOW}🔍 Mode test - Aucune suppression réelle{Colors.RESET}")
            print(f"{Colors.BOLD}Fichiers/dossiers à supprimer:{Colors.RESET}")
            
            for file_path in obsolete_files:
                if file_path.exists():
                    if file_path.is_file():
                        print(f"  {Colors.RED}🗑️ FICHIER: {file_path}{Colors.RESET}")
                    else:
                        print(f"  {Colors.RED}🗑️ DOSSIER: {file_path}{Colors.RESET}")
            
            # Nettoyage des dossiers temporaires (mode test)
            print(f"{Colors.BOLD}Dossiers à vider:{Colors.RESET}")
            for dir_pattern in self.dirs_to_clean:
                dir_path = self.project_root / dir_pattern
                if dir_path.exists():
                    print(f"  {Colors.BLUE}🧹 VIDER: {dir_path}{Colors.RESET}")
            
            return len(obsolete_files)
        
        else:
            # Suppression réelle
            removed_files = self.remove_obsolete_files(obsolete_files)
            
            # Nettoyage des dossiers temporaires
            cleaned_dirs = self.clean_directories()
            
            # Résultats
            print(f"{Colors.GREEN}✅ {len(removed_files)} fichiers/dossiers supprimés{Colors.RESET}")
            print(f"{Colors.BLUE}🧹 {len(cleaned_dirs)} dossiers nettoyés{Colors.RESET}")
            
            # Afficher le détail
            if removed_files:
                print(f"{Colors.BOLD}📋 Détail des suppressions:{Colors.RESET}")
                for file_path in removed_files:
                    print(f"  {Colors.GREEN}✓ {file_path}{Colors.RESET}")
            
            if cleaned_dirs:
                print(f"{Colors.BOLD}📋 Dossiers nettoyés:{Colors.RESET}")
                for dir_path in cleaned_dirs:
                    print(f"  {Colors.BLUE}✓ {dir_path}{Colors.RESET}")
            
            return len(removed_files)

def main():
    """Point d'entrée principal"""
    cleaner = ProjectCleaner()
    
    print(f"{Colors.BOLD}{Colors.MAGENTA}🧹 NETTOYAGE PROJET VANTABLACK v5{Colors.RESET}")
    print(f"{Colors.YELLOW}Suppression des fichiers obsolètes et temporaires{Colors.RESET}")
    
    # D'abord mode test pour voir ce qui sera supprimé
    print(f"\n{Colors.BOLD}🔍 ANALYSE PRELIMINAIRE:{Colors.RESET}")
    count = cleaner.run_cleanup(dry_run=True)
    
    if count == 0:
        print(f"{Colors.GREEN}🎉 Aucun fichier obsolète trouvé ! Le projet est propre.{Colors.RESET}")
        return
    
    # Demander confirmation pour la suppression réelle
    print(f"\n{Colors.YELLOW}➤ Voulez-vous procéder à la suppression ? (o/n): {Colors.RESET}")
    confirmation = input().strip().lower()
    
    if confirmation == 'o':
        print(f"\n{Colors.RED}🗑️ SUPPRESSION EN COURS...{Colors.RESET}")
        cleaner.run_cleanup(dry_run=False)
        print(f"{Colors.GREEN}✅ Nettoyage terminé avec succès !{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}❌ Nettoyage annulé.{Colors.RESET}")

if __name__ == "__main__":
    main()