# Build QualiManager en arrière-plan
$ErrorActionPreference = "Continue"
cd "f:\Applications\Gestion Qualité"

Write-Host "============================================================"
Write-Host "  QualiManager - Build Automatique"
Write-Host "  Ce script va construire l'application en arriere-plan"
Write-Host "============================================================"
Write-Host ""

# Lancer le build dans un processus séparé
$process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c build_quick.bat" -PassThru -WindowStyle Minimized

Write-Host "Build lance en arriere-plan (PID: $($process.Id))"
Write-Host "Patientez 5-8 minutes..."
Write-Host ""

# Attendre que le processus se termine
$process.WaitForExit()

Write-Host ""
Write-Host "============================================================"
Write-Host "  BUILD TERMINE!"
Write-Host "============================================================"
Write-Host ""

# Afficher les résultats
if (Test-Path "output\Portable\QualiManager.exe") {
    $portable = Get-Item "output\Portable\QualiManager.exe"
    Write-Host "✓ Version PORTABLE creee:"
    Write-Host "  Fichier: $($portable.FullName)"
    Write-Host "  Taille: $([math]::Round($portable.Length/1MB,1)) MB"
    Write-Host "  Date: $($portable.LastWriteTime)"
    Write-Host ""
}

if (Test-Path "output\Installer\QualiManager\QualiManager.exe") {
    $installer = Get-Item "output\Installer\QualiManager\QualiManager.exe"
    Write-Host "✓ Version INSTALLEUR creee:"
    Write-Host "  Fichier: $($installer.FullName)"
    Write-Host "  Taille: $([math]::Round($installer.Length/1MB,1)) MB"
    Write-Host "  Date: $($installer.LastWriteTime)"
    Write-Host ""
}

Write-Host "============================================================"
Write-Host ""
pause
