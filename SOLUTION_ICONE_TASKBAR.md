# SOLUTION AU PROBLÈME D'ICÔNE ET NOM DANS LA TASKBAR

## 🔴 PROBLÈME IDENTIFIÉ

Flet utilise une architecture client-serveur où :
- `QualiManager.exe` lance l'application
- Flet démarre `fletd.exe` (daemon Flet) qui crée la vraie fenêtre
- Windows voit `fletd.exe` dans la taskbar, pas `QualiManager.exe`
- Résultat : L'icône et le nom affichés sont ceux de fletd.exe

**C'est une limitation architecturale de Flet, pas un bug de QualiManager.**

## ✅ SOLUTIONS QUI FONCTIONNENT

### Solution 1 : Utiliser le raccourci (RECOMMANDÉ)

1. **Pour la version PORTABLE** :
   - Utilisez le fichier `QualiManager.lnk` qui a été créé
   - Faites glisser ce raccourci vers la taskbar
   - ✅ L'icône et le nom seront corrects !

2. **Pour la version INSTALLEUR** :
   - Après l'installation, un raccourci sera créé dans le menu Démarrer
   - Épinglez depuis le menu Démarrer au lieu de l'exe direct
   - ✅ L'icône et le nom seront corrects !

### Solution 2 : Épingler pendant l'exécution

1. Lancez `QualiManager.exe`
2. Pendant que l'application tourne, faites clic droit sur l'icône dans la taskbar
3. Choisissez "Pin to taskbar"
4. ✅ Le nom et l'icône seront corrects tant que l'app reste épinglée

### Solution 3 : Créer un raccourci manuellement

```powershell
# Si vous voulez créer votre propre raccourci :
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$HOME\Desktop\QualiManager.lnk")
$Shortcut.TargetPath = "C:\Chemin\Vers\QualiManager.exe"
$Shortcut.IconLocation = "C:\Chemin\Vers\icon.ico"
$Shortcut.Description = "QualiManager - Gestion Qualité QHSE"
$Shortcut.Save()
```

## 📝 POURQUOI CE N'EST PAS UN BUG

Flet est conçu pour être multi-plateforme (Windows, Mac, Linux, Web).
Pour y parvenir, il utilise une architecture où :
- L'exe est un "lanceur"
- `fletd` est le "moteur" qui affiche l'interface

Cette architecture permet à Flet d'être flexible, mais elle a cette limitation
sur Windows concernant la taskbar.

## 🎯 RÉSUMÉ

✅ **Les métadonnées de QualiManager.exe sont CORRECTES**
✅ **L'icône est intégrée dans l'exe**
✅ **Le nom du produit est "QualiManager - Gestion Qualité QHSE"**

❌ **Flet utilise fletd.exe qui écrase ces informations au runtime**

✅ **Solution : Utilisez les raccourcis au lieu de l'exe direct**

## 📁 FICHIERS LIVRÉS

- `output/Portable/QualiManager.exe` - Application portable
- `QualiManager.lnk` - Raccourci avec métadonnées correctes (à épingler)
- `output/QualiManager_v2.1.0_Setup.exe` - Installateur (crée automatiquement les raccourcis)
