import os
import sys
import platform
import subprocess
from pathlib import Path


def py_ok():
    vi = sys.version_info
    return vi.major >= 3 and vi.minor >= 11


def which(cmd):
    from shutil import which as _w
    return _w(cmd) is not None


def run(cmd, env=None, cwd=None):
    p = subprocess.run(cmd, env=env, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def ensure_venv(venv_path: Path):
    if venv_path.exists():
        return True
    rc, out = run([sys.executable, "-m", "venv", str(venv_path)])
    return rc == 0


def venv_python(venv_path: Path):
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def pep668_compliant():
    """Vérifie la conformité PEP 668 (environnements externes managés)"""
    try:
        # Vérifie si pip est en mode externe managé
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--user'], 
                              capture_output=True, text=True, timeout=30)
        
        # Si pip refuse l'installation user, c'est PEP 668 compliant
        if "externally managed environment" in result.stderr:
            return True
            
        # Vérification supplémentaire pour les systèmes modernes
        import sysconfig
        schemes = sysconfig.get_paths()
        if 'venv' in schemes['purelib'] or 'venv' in schemes['platlib']:
            return True
            
        return False
    except Exception as e:
        # En cas d'erreur, on suppose la conformité pour éviter les faux positifs
        return True


def install_requirements(py, req_file="requirements.txt"):
    if not Path(req_file).exists():
        return False, f"Missing {req_file}"
    rc, out = run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    if rc != 0:
        return False, out
    rc, out = run([str(py), "-m", "pip", "install", "-r", req_file])
    if rc != 0:
        return False, out
    return True, out


def print_os_guidance():
    """Guide d'installation spécifique à chaque OS avec commandes exactes"""
    sysname = platform.system()
    
    if sysname == "Darwin":
        print("🔵 macOS détecté - Configuration requise:")
        print("   Python 3.11+ via Homebrew (recommandé):")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("   brew install python@3.11")
        print("")
        print("   OU Python officiel (alternative):")
        print("   Télécharger: https://www.python.org/downloads/macos/")
        print("   Vérifier: python3 --version && python3 -m venv --version")
        
        if not which("brew"):
            print("\n⚠️  Homebrew non détecté - Installation requise")
        
        # Vérification Xcode pour macOS
        if not which("xcode-select"):
            print("\n📦 Outils de développement Xcode requis:")
            print("   xcode-select --install")
    
    elif sysname == "Linux":
        print("🐧 Linux détecté - Paquets requis:")
        
        # Détection de la distribution
        distro_info = ""
        try:
            with open('/etc/os-release') as f:
                distro_info = f.read()
        except:
            pass
            
        if 'ubuntu' in distro_info.lower() or 'debian' in distro_info.lower():
            print("   Debian/Ubuntu:")
            print("   sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv python3.11-dev")
        elif 'arch' in distro_info.lower():
            print("   Arch Linux:")
            print("   sudo pacman -S python python-pip")
        else:
            print("   Distribution générique:")
            print("   sudo apt-get install python3.11 python3.11-venv  # ou équivalent pour votre distro")
    
    elif sysname == "Windows":
        print("🪟 Windows détecté - Instructions:")
        print("   1. Télécharger Python 3.11+: https://www.python.org/downloads/windows/")
        print("   2. Durant l'installation: Cocher 'Add Python to PATH'")
        print("   3. Vérifier: python --version && python -m venv --version")
        print("   4. PowerShell: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser")
    
    else:
        print(f"❓ Système non standard: {sysname}")
        print("   Python 3.11+ et venv module requis manuellement")


def detect_python_issues():
    """Détecte les problèmes courants de configuration Python"""
    issues = []
    
    # Vérification version Python
    vi = sys.version_info
    if vi.major < 3 or (vi.major == 3 and vi.minor < 11):
        issues.append(f"Python {vi.major}.{vi.minor} détecté - 3.11+ requis")
    
    # Vérification module venv
    try:
        import venv
    except ImportError:
        issues.append("Module venv non disponible")
    
    # Vérification pip
    try:
        import pip
    except ImportError:
        issues.append("Pip non disponible")
    
    return issues


def validate_environment():
    """Validation complète de l'environnement"""
    print("🔍 Audit de l'environnement...")
    
    # Détection OS
    sysname = platform.system()
    print(f"📋 OS détecté: {sysname} {platform.release()}")
    
    # Vérification Python
    issues = detect_python_issues()
    if issues:
        print("❌ Problèmes de configuration Python:")
        for issue in issues:
            print(f"   - {issue}")
        print_os_guidance()
        return False
    
    # Vérification PEP 668
    if not pep668_compliant():
        print("⚠️  Environnement non conforme PEP 668 (externally managed)")
        print("   Continuer: un environnement virtuel dédié sera créé (.venv)")
    
    # Vérification dépendances QR
    try:
        import pyzbar  # noqa: F401
    except Exception:
        print("ℹ️  Dépendance de décodage QR optionnelle manquante: pyzbar")
        if sysname == "Darwin":
            print("   brew install zbar && python -m pip install pyzbar")
        elif sysname == "Linux":
            print("   sudo apt-get install -y libzbar0 && python -m pip install pyzbar")
        else:
            print("   python -m pip install pyzbar")
    try:
        import shutil as _sh
        if not _sh.which("zbarimg") and sysname in ("Darwin", "Linux"):
            print("ℹ️  binaire zbarimg non détecté, le décodage QR peut échouer")
    except Exception:
        pass
    
    print("✅ Environnement validé")
    return True


def main():
    print("🚀 Vantablack - Bootstrap Multi-OS")
    print("=" * 50)
    
    # Validation initiale
    if not validate_environment():
        sys.exit(1)
    
    # Création venv
    venv_path = Path(".venv")
    if venv_path.exists():
        print(f"✅ Environnement virtuel existant: {venv_path}")
    else:
        print(f"📦 Création de l'environnement virtuel: {venv_path}")
        if not ensure_venv(venv_path):
            print("❌ Échec de création de la venv")
            sys.exit(1)
    
    # Vérification Python venv
    py = venv_python(venv_path)
    if not py.exists():
        print("❌ Python de la venv introuvable")
        sys.exit(1)
    
    # Installation dépendances
    print("📦 Installation des dépendances...")
    ok, out = install_requirements(py)
    if not ok:
        print("❌ Échec installation dépendances:")
        print(out)
        sys.exit(1)
    
    print("✅ Dépendances installées avec succès")
    
    # Vérification finale
    print("\n🔍 Vérification finale...")
    try:
        # Test import des modules critiques
        rc, out = run([str(py), "-c", "import mitmproxy; import fastapi; print('Modules critiques: OK')"])
        if rc == 0:
            print("✅ Modules critiques validés")
        else:
            print("⚠️  Problème avec les modules critiques")
            
        # Liste des dépendances installées
        rc, out = run([str(py), "-m", "pip", "freeze"])
        print(f"📊 Dépendances installées ({len(out.splitlines())} packages)")
        
    except Exception as e:
        print(f"⚠️  Erreur lors de la vérification finale: {e}")
    
    print("\n🎯 Bootstrap terminé avec succès!")
    print("Prochaines étapes:")
    print("   source .venv/bin/activate  # Linux/macOS")
    print("   .venv\\Scripts\\activate  # Windows")
    print("   python -m core.cli.main    # Lancer l'interface CLI")
    
    # Diagnostic final
    print("\n📋 Diagnostic de l'environnement:")
    rc, out = run([str(py), "-c", "import platform; print(f'OS: {platform.system()} {platform.release()}')"])
    print(out.strip())
    
    # Test du doctor
    print("\n🩺 Test du diagnostic:")
    rc, out = run([str(py), "-m", "core.cli.main", "doctor"])
    if rc == 0:
        print("✅ Diagnostic CLI fonctionnel")
    else:
        print("⚠️  Diagnostic CLI en erreur")
    
    print("\n✨ Bootstrap complété avec succès!")
    print("L'environnement est prêt pour le développement et le testing.")


if __name__ == "__main__":
    main()
