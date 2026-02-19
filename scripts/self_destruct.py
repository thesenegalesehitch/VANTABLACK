import os
import sys
import shutil
from pathlib import Path
import time

def is_repo_root(p: Path) -> bool:
    if not p.exists() or not p.is_dir():
        return False
    if p == p.root:
        return False
    if len(p.parts) < 3:
        return False
    if not (p / ".git").exists() and not (p / "core").exists():
        return False
    marker = {"core", "phishlets", "requirements-v5.txt"}
    present = [x for x in marker if (p / x).exists()]
    return len(present) >= 2

def confirm_allowed() -> None:
    env = os.environ.get("CONFIRM_SELF_DESTRUCT", "")
    if env != "YES":
        print("CONFIRM_SELF_DESTRUCT=YES requis")
        sys.exit(2)
    try:
        phrase = input("Tape 'DELETE' pour confirmer: ").strip()
    except EOFError:
        phrase = ""
    if phrase != "DELETE":
        print("Confirmation invalide")
        sys.exit(2)

def main():
    here = Path(__file__).resolve()
    root = here.parents[1]
    if not is_repo_root(root):
        print("Racine invalide")
        sys.exit(2)
    dry = True
    force = False
    for a in sys.argv[1:]:
        if a == "--force":
            force = True
        if a == "--no-dry-run":
            dry = False
    print(f"Cible: {root}")
    if dry:
        print("Dry-run: aucun fichier supprimé")
        for i, p in enumerate(root.iterdir()):
            if i > 20:
                print("…")
                break
            print(f"- {p.name}")
        print("Ajoute --no-dry-run pour activer la suppression")
        sys.exit(0)
    if not force:
        print("Utilise --force pour confirmer l'exécution")
        sys.exit(2)
    confirm_allowed()
    print("Suppression dans 5s… Ctrl+C pour annuler")
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("Annulé")
        sys.exit(1)
    try:
        shutil.rmtree(str(root))
        print("Projet supprimé")
    except Exception as e:
        print(f"Échec: {e}")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
