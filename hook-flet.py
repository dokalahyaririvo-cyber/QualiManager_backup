# Hook PyInstaller personnalisé pour Flet
# Force l'utilisation des métadonnées de l'application principale

from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collecter tous les fichiers Flet
datas, binaries, hiddenimports = collect_all('flet')

# Ajouter les fichiers fletd avec nos métadonnées
datas += collect_data_files('flet.flet')
