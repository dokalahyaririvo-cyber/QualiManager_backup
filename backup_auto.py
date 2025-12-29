"""Sauvegarde automatique du projet QualiManager.

Lance une sauvegarde horodatée toutes les `INTERVAL_HOURS` heures (par défaut: 2h).
Peut aussi être exécuté manuellement pour une sauvegarde immédiate.
"""
import shutil
import os
from datetime import datetime
import time
import threading
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ROOT_DIR  # Sauvegarder le projet courant
BACKUP_BASE_DIR = Path(r"F:\Sauvegardes_QualiManager")  # Adaptez si besoin
INTERVAL_HOURS = 2  # Sauvegarde toutes les 2 heures (minimum demandé)

# Dossiers/fichiers à exclure de la sauvegarde
EXCLUDE_DIRS = {"build", "output", "exports", "__pycache__", ".git", "venv", "env"}
EXCLUDE_PATTERNS = {"*.pyc", "*.log", "*.db"}


def create_backup():
    """Crée une sauvegarde horodatée du projet."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_BASE_DIR / f"QualiManager_Backup_{timestamp}"

    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Début de la sauvegarde...")

        # Créer le dossier de sauvegarde s'il n'existe pas
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Copier les fichiers en excluant certains dossiers
        for item in SOURCE_DIR.iterdir():
            if item.name in EXCLUDE_DIRS:
                continue

            dest = backup_dir / item.name

            if item.is_dir():
                shutil.copytree(
                    item,
                    dest,
                    ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS, "__pycache__"),
                    dirs_exist_ok=False,
                )
            else:
                shutil.copy2(item, dest)

        print(f"✓ Sauvegarde créée : {backup_dir}")
        cleanup_old_backups()

    except Exception as e:
        print(f"✗ Erreur lors de la sauvegarde : {e}")


def cleanup_old_backups(keep_last=10):
    """Garde seulement les N dernières sauvegardes."""
    if not BACKUP_BASE_DIR.exists():
        return

    backups = sorted(
        [d for d in BACKUP_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("QualiManager_Backup_")],
        key=lambda p: p.name,
        reverse=True,
    )

    for old_backup in backups[keep_last:]:
        try:
            shutil.rmtree(old_backup)
            print(f"  Ancienne sauvegarde supprimée : {old_backup.name}")
        except Exception as e:
            print(f"  Impossible de supprimer {old_backup.name}: {e}")


def backup_loop():
    """Boucle de sauvegarde qui s'exécute toutes les X heures."""
    while True:
        create_backup()
        time.sleep(max(1, INTERVAL_HOURS) * 3600)  # Sécurité: pas moins d'1h


def main():
    """Lance le système de sauvegarde automatique"""
    print("=" * 60)
    print("  SAUVEGARDE AUTOMATIQUE QUALIMANAGER")
    print("=" * 60)
    print(f"Source      : {SOURCE_DIR}")
    print(f"Destination : {BACKUP_BASE_DIR}")
    print(f"Fréquence   : Toutes les {INTERVAL_HOURS} heure(s)")
    print(f"Exclusions  : {', '.join(EXCLUDE_DIRS)}")
    print("=" * 60)
    print("\nAppuyez sur Ctrl+C pour arrêter\n")
    
    # Lancer la boucle de sauvegarde dans un thread
    backup_thread = threading.Thread(target=backup_loop, daemon=True)
    backup_thread.start()
    
    # Garder le programme actif
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSauvegarde automatique arrêtée par l'utilisateur.")
