; ============================================
; Ultra Font Installer - Script Inno Setup
; ============================================
; Auteur: JULAI
; Version: 2.0.0
; Ce script crée un installateur Windows complet
; ============================================

#define MyAppName "Ultra Font Installer"
#define MyAppVersion "2.0.0"
#define MyAppPublisher "JULAI"
#define MyAppURL "https://github.com/Ulai12/Font-Ultra-Installer"
#define MyAppExeName "Ultra Font Installer.exe"
#define MyAppAssocName "Police"
#define MyAppAssocExt ".ttf"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; Identifiant unique de l'application (généré avec GUID)
AppId={{8A5C7E3F-4B2D-4A1E-9F8C-6D3E2B1A0F9E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Répertoire d'installation par défaut
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Autoriser l'utilisateur à changer le répertoire
AllowNoIcons=yes
DisableProgramGroupPage=yes

; Fichier de licence (optionnel - décommenter si vous avez un fichier LICENSE)
; LicenseFile=LICENSE.txt

; Fichiers de sortie
OutputDir=dist
OutputBaseFilename=Ultra_Font_Installer_Setup_v{#MyAppVersion}

; Icône de l'installateur
SetupIconFile=assets\logo.ico

; Compression maximale
Compression=lzma2/ultra64
SolidCompression=yes

; Style Windows moderne
WizardStyle=modern

; Demander les droits administrateur (nécessaire pour installer des polices)
PrivilegesRequired=admin

; Informations de version
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Installateur de polices moderne pour Windows
VersionInfoCopyright=© 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Désinstallation
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Options proposées à l'utilisateur pendant l'installation
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Fichier exécutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Fichier de paramètres (sera créé par l'application si absent)
; Source: "settings.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

[Icons]
; Raccourci dans le menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Raccourci sur le Bureau (si l'option est cochée)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Raccourci dans la barre de lancement rapide (si l'option est cochée)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Association des fichiers .ttf avec l'application (optionnel)
; Décommenter pour activer l'association de fichiers
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
; Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Run]
; Lancer l'application après l'installation (si l'utilisateur le souhaite)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runascurrentuser

[Code]
// ============================================
// Code Pascal pour des fonctionnalités avancées
// ============================================

// Fonction appelée lors de la désinstallation
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  SettingsPath: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Demander si l'utilisateur veut supprimer les paramètres
    SettingsPath := ExpandConstant('{app}\settings.json');
    if FileExists(SettingsPath) then
    begin
      if MsgBox('Voulez-vous supprimer également les paramètres de l''application ?',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        DeleteFile(SettingsPath);
      end;
    end;
  end;
end;

// Vérifier si l'application est déjà en cours d'exécution
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;

  // Vérifier si l'application est en cours d'exécution
  if Exec('tasklist', '/FI "IMAGENAME eq Ultra Font Installer.exe" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    // L'application pourrait être en cours d'exécution, avertir l'utilisateur
  end;
end;

// Afficher un message de bienvenue personnalisé
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;
