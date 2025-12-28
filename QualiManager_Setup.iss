; Script d'installation QualiManager
; Version 2.1.0
; Nécessite Inno Setup 6.0 ou supérieur

#define MyAppName "QualiManager"
#define MyAppVersion "2.1.0"
#define MyAppPublisher "Votre Société"
#define MyAppURL "https://www.example.com/"
#define MyAppExeName "QualiManager_Dir.exe"

[Setup]
AppId={{B5D8F6E3-7A2C-4B9E-8D1F-3C4A5B6E7F8A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={commonpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=output
OutputBaseFilename=QualiManager_v{#MyAppVersion}_Setup
;SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Application principale
Source: "QualiManager\QualiManager_Dir.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "QualiManager\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

; Base de données template (vide)
Source: "..\..\qualimanager_erp.db"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "..\..\GUIDE_INSTALLATION.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_MISE_A_JOUR.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_DISTRIBUTION.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_IMPORT_EXCEL.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_IMPORT_EXPORT_NC.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_IMPORT_EXPORT_VEILLE.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_NOUVELLES_FONCTIONS_NC.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\GUIDE_RAPIDE_EXPORT_IMPORT.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\..\LICENSE.txt"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  // Message d'information sur l'architecture double localisation
  WizardForm.WelcomeLabel2.Caption := 
    'Cet assistant vous guidera dans l''installation de QualiManager v2.1.0.' + #13#10#13#10 +
    'REMARQUE : Les données de l''application seront stockées dans :' + #13#10 +
    ExpandConstant('{userappdata}\QualiManager') + #13#10#13#10 +
    'Cliquez sur Suivant pour continuer.';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Créer le dossier AppData pour l'utilisateur
    AppDataPath := ExpandConstant('{userappdata}\QualiManager');
    if not DirExists(AppDataPath) then
    begin
      CreateDir(AppDataPath);
      CreateDir(AppDataPath + '\backups');
    end;
    
    // Copier la base de données template si elle n'existe pas déjà
    if not FileExists(AppDataPath + '\qualimanager_erp.db') then
    begin
      FileCopy(ExpandConstant('{app}\qualimanager_erp.db'), 
               AppDataPath + '\qualimanager_erp.db', False);
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  Response: Integer;
begin
  // Demander si l'utilisateur veut conserver les données
  Response := MsgBox('Voulez-vous également supprimer les données de l''application ?' + #13#10 +
                     '(Base de données et sauvegardes dans AppData)' + #13#10#13#10 +
                     'Cliquez sur Oui pour tout supprimer, Non pour conserver les données.', 
                     mbConfirmation, MB_YESNO);
  
  if Response = IDYES then
  begin
    // Supprimer le dossier AppData
    DelTree(ExpandConstant('{userappdata}\QualiManager'), True, True, True);
  end;
  
  Result := True;
end;
