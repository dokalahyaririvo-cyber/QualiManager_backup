<#
Script d’automatisation GitHub pour QualiManager.
- Initialise git (si besoin)
- Crée/complète .gitignore avec les dossiers volumineux
- Configure l’utilisateur git (si valeurs fournies)
- Ajoute le remote (si non présent)
- Commit + push avec message horodaté

Utilisation (PowerShell) :
    powershell -ExecutionPolicy Bypass -File .\github_backup.ps1 -RepoUrl "https://github.com/USER/REPO.git" -Branch "main" -UserName "Votre Nom" -UserEmail "vous@example.com"

Prérequis :
- Git installé et dans le PATH
- Authentification :
  * HTTPS : Git vous demandera token/mot de passe (PAT recommandé)
  * SSH : ajoutez plutôt le remote en ssh (git@github.com:USER/REPO.git) et assurez-vous que votre clé est chargée
#>

param(
    [Parameter(Mandatory=$true)] [string]$RepoUrl,
    [string]$Branch = "main",
    [string]$UserName,
    [string]$UserEmail
)

function Ensure-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Commande requise introuvable: $Name"
    }
}

function Ensure-GitIgnore {
    param([string]$Path)
    $entries = @(
        "build/",
        "output/",
        "exports/",
        "venv/",
        "env/",
        "__pycache__/",
        ".git/",
        "*.log",
        "*.db",
        "*.pyc"
    )
    if (-not (Test-Path $Path)) {
        $entries -join "`n" | Out-File -FilePath $Path -Encoding UTF8
        return
    }
    $existing = Get-Content $Path -ErrorAction SilentlyContinue
    $toAdd = $entries | Where-Object { $_ -notin $existing }
    if ($toAdd.Count -gt 0) {
        Add-Content -Path $Path -Value ($toAdd -join "`n")
    }
}

function Run-Git {
    param([string[]]$Args)
    & git @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') a echoue (code $LASTEXITCODE)"
    }
}

try {
    Ensure-Command -Name "git"

    $root = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $root

    # Init repo si besoin
    if (-not (Test-Path .git)) {
        Run-Git @("init")
    }

    # Config user si fourni
    if ($UserName) { Run-Git @("config", "user.name", $UserName) }
    if ($UserEmail) { Run-Git @("config", "user.email", $UserEmail) }

    # .gitignore
    Ensure-GitIgnore "$root\.gitignore"

    # Remote
    $remotes = git remote -v 2>$null
    if ($remotes -notmatch "origin") {
        Run-Git @("remote", "add", "origin", $RepoUrl)
    }

    # Add + commit
    Run-Git @("add", ".")
    $message = "Backup $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Run-Git @("commit", "-m", $message)

    # Push
    Run-Git @("push", "origin", $Branch)

    Write-Host "`nSucces : backup pousse sur $RepoUrl ($Branch)." -ForegroundColor Green
    Write-Host "Si authentification HTTPS, utilisez un token PAT (recommande) quand Git le demande." -ForegroundColor Yellow
}
catch {
    Write-Error $_
    exit 1
}
