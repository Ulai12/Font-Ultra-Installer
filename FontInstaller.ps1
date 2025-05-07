<#
.SYNOPSIS
   GUI PowerShell Font Installer avec annulation, logs et section crédits.
.DESCRIPTION
   - Parcourt un dossier sélectionné pour installer .ttf, .otf, .fon, .woff
   - Affiche une barre de progression et permet d'annuler le processus
   - Garde un log détaillé dans un fichier
   - Affiche une section crédits
#>

#region Configuration
# Constantes
$script:CONFIG = @{
    WindowTitle = "Font Installer"
    WindowWidth = 800
    WindowHeight = 600
    Version = "1.0"
    Author = "JULAI GAVENOU"
    SupportedExtensions = @('.ttf', '.otf', '.fon', '.woff', '.woff2')
    UpdateCheckUrl = "https://api.github.com/repos/yourusername/fontinstaller/releases/latest"
    Theme = "Light" # Light ou Dark
}

# Dictionnaire des traductions
$script:TRANSLATIONS = @{
    'fr' = @{
        'WindowTitle' = "Installateur de polices"
        'BrowseButton' = "Parcourir..."
        'CancelButton' = "Annuler"
        'NoFolderSelected' = "Aucun dossier sélectionné"
        'Ready' = "Prêt."
        'Installing' = "Installation en cours..."
        'Processing' = "Traitement {0}/{1}"
        'Cancelled' = "Installation annulée."
        'Completed' = "Terminé!"
        'NoFontsFound' = "Aucune police trouvée dans le dossier sélectionné."
        'AdminRequired' = "Ce programme nécessite des droits administrateur."
        'SuccessMessage' = "{0} polices ont été installées avec succès."
        'DevelopedBy' = "Développé par {0} | Font Installer v{1}"
        'RestartMessage' = "Pour que les nouvelles polices soient disponibles, vous devez redémarrer l'explorateur de fichiers ou votre PC."
        'RestartExplorer' = "Redémarrer l'explorateur"
        'RestartPC' = "Redémarrer le PC"
        'Cancel' = "Annuler"
        'InstalledFonts' = "Polices installées"
        'AlreadyInstalled' = "Déjà installées"
        'FailedFonts' = "Échecs d'installation"
        'OpenFontsFolder' = "Ouvrir le dossier des polices"
        'UpdateAvailable' = "Une mise à jour est disponible (v{0})"
        'UpdateNow' = "Mettre à jour maintenant"
        'UpdateLater' = "Plus tard"
        'DragDropMessage' = "Glissez-déposez vos polices ici"
        'ThemeLight' = "Thème clair"
        'ThemeDark' = "Thème sombre"
    }
    'en' = @{
        'WindowTitle' = "Font Installer"
        'BrowseButton' = "Browse..."
        'CancelButton' = "Cancel"
        'NoFolderSelected' = "No folder selected"
        'Ready' = "Ready."
        'Installing' = "Installing..."
        'Processing' = "Processing {0}/{1}"
        'Cancelled' = "Installation cancelled."
        'Completed' = "Completed!"
        'NoFontsFound' = "No fonts found in selected folder."
        'AdminRequired' = "This program requires administrator rights."
        'SuccessMessage' = "{0} fonts have been successfully installed."
        'DevelopedBy' = "Developed by {0} | Font Installer v{1}"
        'RestartMessage' = "To make the new fonts available, you need to restart File Explorer or your PC."
        'RestartExplorer' = "Restart Explorer"
        'RestartPC' = "Restart PC"
        'Cancel' = "Cancel"
        'InstalledFonts' = "Installed fonts"
        'AlreadyInstalled' = "Already installed"
        'FailedFonts' = "Installation failed"
        'OpenFontsFolder' = "Open fonts folder"
        'UpdateAvailable' = "An update is available (v{0})"
        'UpdateNow' = "Update now"
        'UpdateLater' = "Later"
        'DragDropMessage' = "Drag and drop your fonts here"
        'ThemeLight' = "Light theme"
        'ThemeDark' = "Dark theme"
    }
}

# Détection de la langue du système et configuration de la langue par défaut
$script:CurrentLanguage = (Get-Culture).TwoLetterISOLanguageName
if (-not $script:TRANSLATIONS.ContainsKey($script:CurrentLanguage)) {
    $script:CurrentLanguage = 'en' # Langue par défaut si non supportée
}

# Variables globales
$script:cancelRequested = $false
$script:logFile = "$env:TEMP\FontInstaller_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
#endregion

#region Fonctions utilitaires
function Test-AdminRights {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Font {
    param(
        [System.IO.FileInfo]$Font
    )
    try {
        if (-not (Test-FontFile -Font $Font)) {
            Write-Log "Fichier police invalide: $($Font.Name)"
            $listView.Items.Add([PSCustomObject]@{
                Name = $Font.Name
                Status = "Échec"
                Type = $Font.Extension
            })
            return $false
        }
        
        $dest = Join-Path $env:WINDIR\Fonts $Font.Name
        if (-not (Test-Path $dest)) {
            Copy-Item -Path $Font.FullName -Destination $dest -ErrorAction Stop
            $regName = if ($Font.Extension -ieq '.otf') { 
                "$($Font.BaseName) (OpenType)" 
            } else { 
                "$($Font.BaseName) (TrueType)" 
            }
            New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' `
                            -Name $regName -PropertyType String -Value $Font.Name -Force | Out-Null
            Write-Log "Installé: $($Font.Name)"
            $listView.Items.Add([PSCustomObject]@{
                Name = $Font.Name
                Status = "Installé"
                Type = $Font.Extension
            })
            return $true
        }
        Write-Log "Déjà installé: $($Font.Name)"
        $listView.Items.Add([PSCustomObject]@{
            Name = $Font.Name
            Status = "Déjà installé"
            Type = $Font.Extension
        })
        return $true
    }
    catch {
        Write-Log "Erreur critique lors de l'installation de $($Font.Name): $_"
        $listView.Items.Add([PSCustomObject]@{
            Name = $Font.Name
            Status = "Échec"
            Type = $Font.Extension
        })
        [System.Windows.Forms.MessageBox]::Show(
            "Erreur lors de l'installation de $($Font.Name)",
            "Erreur",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error)
        return $false
    }
}

function Test-FontFile {
    param(
        [System.IO.FileInfo]$Font
    )
    try {
        $stream = [System.IO.File]::OpenRead($Font.FullName)
        if ($Font.Extension -ieq '.ttf' -or $Font.Extension -ieq '.otf') {
            # Vérification de la signature des polices
            $buffer = New-Object byte[] 4
            $stream.Read($buffer, 0, 4) | Out-Null
            $signature = [System.Text.Encoding]::ASCII.GetString($buffer)
            $stream.Close()
            
            return $signature -match '(OTTO|true|typ1)'
        }
        $stream.Close()
        return $true
    }
    catch {
        Write-Log "Erreur de validation pour $($Font.Name): $_"
        return $false
    }
}

function Get-TranslatedText {
    param(
        [string]$Key,
        [array]$Parameters = @()
    )
    
    $text = $script:TRANSLATIONS[$script:CurrentLanguage][$Key]
    if ($Parameters.Count -gt 0) {
        $text = [string]::Format($text, $Parameters)
    }
    return $text
}

function Save-UserPreferences {
    $prefPath = Join-Path $env:APPDATA "FontInstaller\preferences.json"
    $prefs = @{
        LastLanguage = $script:CurrentLanguage
        LastFolder = $lblFolder.Text
    }
    
    try {
        $prefDir = Split-Path $prefPath -Parent
        if (-not (Test-Path $prefDir)) {
            New-Item -ItemType Directory -Path $prefDir | Out-Null
        }
        $prefs | ConvertTo-Json | Set-Content $prefPath
        Write-Log "Préférences sauvegardées"
    }
    catch {
        Write-Log "Erreur lors de la sauvegarde des préférences: $_"
    }
}
#endregion

#region Initialisation
# Vérification des droits admin
if (-not (Test-AdminRights)) {
    [System.Windows.Forms.MessageBox]::Show(
        $script:TRANSLATIONS[$script:CurrentLanguage]['AdminRequired'],
        "Erreur",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

# Chargement des assemblies
try {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
}
catch {
    Write-Error "Impossible de charger les assemblies nécessaires: $_"
    exit 1
}
#endregion

# Fonction de log
function Write-Log {
    param([string]$message)
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $entry = "$timestamp - $message"
    Add-Content -Path $script:logFile -Value $entry
    Write-Host $entry
}

# Création de la fenêtre
$form = New-Object System.Windows.Forms.Form
$form.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['WindowTitle']
$form.Size = New-Object System.Drawing.Size($script:CONFIG.WindowWidth, $script:CONFIG.WindowHeight)
$form.StartPosition = 'CenterScreen'
$form.AllowDrop = $true

# Application du thème
function Apply-Theme {
    param($form)
    if ($script:CONFIG.Theme -eq "Dark") {
        $form.BackColor = [System.Drawing.Color]::FromArgb(45, 45, 48)
        $form.ForeColor = [System.Drawing.Color]::White
        foreach ($control in $form.Controls) {
            if ($control -is [System.Windows.Forms.Button]) {
                $control.BackColor = [System.Drawing.Color]::FromArgb(60, 60, 63)
                $control.ForeColor = [System.Drawing.Color]::White
            }
            elseif ($control -is [System.Windows.Forms.Label]) {
                $control.ForeColor = [System.Drawing.Color]::White
            }
        }
    }
    else {
        $form.BackColor = [System.Drawing.SystemColors]::Control
        $form.ForeColor = [System.Drawing.SystemColors]::ControlText
        foreach ($control in $form.Controls) {
            if ($control -is [System.Windows.Forms.Button]) {
                $control.BackColor = [System.Drawing.SystemColors]::Control
                $control.ForeColor = [System.Drawing.SystemColors]::ControlText
            }
            elseif ($control -is [System.Windows.Forms.Label]) {
                $control.ForeColor = [System.Drawing.SystemColors]::ControlText
            }
        }
    }
}

# Liste des polices installées
$listView = New-Object System.Windows.Forms.ListView
$listView.Location = New-Object System.Drawing.Point(20, 150)
$listView.Size = New-Object System.Drawing.Size(740, 300)
$listView.View = [System.Windows.Forms.View]::Details
$listView.FullRowSelect = $true
$listView.GridLines = $true
$listView.Columns.Add("Nom", 200)
$listView.Columns.Add("Statut", 100)
$listView.Columns.Add("Type", 100)
$form.Controls.Add($listView)

# Bouton pour ouvrir le dossier des polices
$btnOpenFontsFolder = New-Object System.Windows.Forms.Button
$btnOpenFontsFolder.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['OpenFontsFolder']
$btnOpenFontsFolder.Location = New-Object System.Drawing.Point(20, 460)
$btnOpenFontsFolder.Size = New-Object System.Drawing.Size(200, 30)
$btnOpenFontsFolder.Add_Click({
    Start-Process "explorer.exe" -ArgumentList "$env:WINDIR\Fonts"
})
$form.Controls.Add($btnOpenFontsFolder)

# Bouton de changement de thème
$btnTheme = New-Object System.Windows.Forms.Button
$btnTheme.Text = if ($script:CONFIG.Theme -eq "Light") { $script:TRANSLATIONS[$script:CurrentLanguage]['ThemeDark'] } else { $script:TRANSLATIONS[$script:CurrentLanguage]['ThemeLight'] }
$btnTheme.Location = New-Object System.Drawing.Point(560, 460)
$btnTheme.Size = New-Object System.Drawing.Size(200, 30)
$btnTheme.Add_Click({
    $script:CONFIG.Theme = if ($script:CONFIG.Theme -eq "Light") { "Dark" } else { "Light" }
    $btnTheme.Text = if ($script:CONFIG.Theme -eq "Light") { $script:TRANSLATIONS[$script:CurrentLanguage]['ThemeDark'] } else { $script:TRANSLATIONS[$script:CurrentLanguage]['ThemeLight'] }
    Apply-Theme $form
})
$form.Controls.Add($btnTheme)

# Gestion du glisser-déposer
$form.Add_DragEnter({
    param($sender, $e)
    if ($e.Data.GetDataPresent([Windows.Forms.DataFormats]::FileDrop)) {
        $e.Effect = [Windows.Forms.DragDropEffects]::Copy
    }
})

$form.Add_DragDrop({
    param($sender, $e)
    $files = $e.Data.GetData([Windows.Forms.DataFormats]::FileDrop)
    if ($files) {
        $folder = if ((Get-Item $files[0]) -is [System.IO.DirectoryInfo]) {
            $files[0]
        } else {
            Split-Path $files[0]
        }
        $lblFolder.Text = $folder
        # Déclencher l'installation
        $btnBrowse.PerformClick()
    }
})

# Vérification des mises à jour
function Check-ForUpdates {
    try {
        $response = Invoke-RestMethod -Uri $script:CONFIG.UpdateCheckUrl
        $latestVersion = $response.tag_name.TrimStart('v')
        if ($latestVersion -gt $script:CONFIG.Version) {
            $result = [System.Windows.Forms.MessageBox]::Show(
                [string]::Format($script:TRANSLATIONS[$script:CurrentLanguage]['UpdateAvailable'], $latestVersion),
                "Mise à jour disponible",
                [System.Windows.Forms.MessageBoxButtons]::YesNo,
                [System.Windows.Forms.MessageBoxIcon]::Information
            )
            if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
                Start-Process $response.html_url
            }
        }
    }
    catch {
        Write-Log "Erreur lors de la vérification des mises à jour: $_"
    }
}

# Label dossier
$lblFolder = New-Object System.Windows.Forms.Label
$lblFolder.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['NoFolderSelected']
$lblFolder.AutoSize = $true
$lblFolder.Location = New-Object System.Drawing.Point(20,20)
$form.Controls.Add($lblFolder)

# Bouton Parcourir
$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['BrowseButton']
$btnBrowse.Size = New-Object System.Drawing.Size(100,30)
$btnBrowse.Location = New-Object System.Drawing.Point(420,15)
$form.Controls.Add($btnBrowse)

# Barre de progression
$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Location = New-Object System.Drawing.Point(20,80)
$progress.Size = New-Object System.Drawing.Size(500,23)
$progress.Style = 'Continuous'
$form.Controls.Add($progress)

# Label statut
$lblStatus = New-Object System.Windows.Forms.Label
$lblStatus.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['Ready']
$lblStatus.AutoSize = $true
$lblStatus.Location = New-Object System.Drawing.Point(20,120)
$form.Controls.Add($lblStatus)

# Bouton Annuler
$btnCancel = New-Object System.Windows.Forms.Button
$btnCancel.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['CancelButton']
$btnCancel.Size = New-Object System.Drawing.Size(100,30)
$btnCancel.Location = New-Object System.Drawing.Point(420,75)
$btnCancel.Enabled = $false
$form.Controls.Add($btnCancel)

# Texte crédits
$lblCredits = New-Object System.Windows.Forms.Label
$lblCredits.Text = [string]::Format($script:TRANSLATIONS[$script:CurrentLanguage]['DevelopedBy'], $script:CONFIG.Author, $script:CONFIG.Version)
$lblCredits.AutoSize = $true
$lblCredits.Location = New-Object System.Drawing.Point(20,220)
$form.Controls.Add($lblCredits)

# Sélecteur de langue
$comboLanguage = New-Object System.Windows.Forms.ComboBox
$comboLanguage.Location = New-Object System.Drawing.Point(420,220)
$comboLanguage.Size = New-Object System.Drawing.Size(100,30)
$comboLanguage.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
$script:TRANSLATIONS.Keys | ForEach-Object { 
    [void]$comboLanguage.Items.Add($_) 
}
$comboLanguage.SelectedItem = $script:CurrentLanguage
$form.Controls.Add($comboLanguage)

# Gestionnaire d'événement pour le changement de langue
$comboLanguage.Add_SelectedIndexChanged({
    $script:CurrentLanguage = $comboLanguage.SelectedItem
    
    # Mise à jour des textes de l'interface
    $form.Text = Get-TranslatedText 'WindowTitle'
    $btnBrowse.Text = Get-TranslatedText 'BrowseButton'
    $btnCancel.Text = Get-TranslatedText 'CancelButton'
    $lblFolder.Text = Get-TranslatedText 'NoFolderSelected'
    $lblStatus.Text = Get-TranslatedText 'Ready'
    $lblCredits.Text = Get-TranslatedText 'DevelopedBy' -Parameters @($script:CONFIG.Author, $script:CONFIG.Version)
})

# Mise à jour des contrôles existants
$form.Text = Get-TranslatedText 'WindowTitle'
$btnBrowse.Text = Get-TranslatedText 'BrowseButton'
$btnCancel.Text = Get-TranslatedText 'CancelButton'
$lblFolder.Text = Get-TranslatedText 'NoFolderSelected'
$lblStatus.Text = Get-TranslatedText 'Ready'
$lblCredits.Text = Get-TranslatedText 'DevelopedBy' -Parameters @($script:CONFIG.Author, $script:CONFIG.Version)

# Action Annuler
$btnCancel.Add_Click({
    $script:cancelRequested = $true
    Write-Log "Annulation demandée par l'utilisateur"
    $lblStatus.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['Cancelled']
})

#region Gestionnaires d'événements
$btnBrowse.Add_Click({
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($dialog.ShowDialog() -ne 'OK') { return }
    
    $folder = $dialog.SelectedPath
    $lblFolder.Text = $folder
    Write-Log "Dossier sélectionné: $folder"

    # Recherche des polices avec pattern matching amélioré
    $FontFiles = Get-ChildItem -Path $folder -Include $CONFIG.SupportedExtensions -File -Recurse
    $total = $FontFiles.Count

    if ($total -eq 0) {
        [System.Windows.Forms.MessageBox]::Show(
            $script:TRANSLATIONS[$script:CurrentLanguage]['NoFontsFound'],
            "Information",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information)
        Write-Log "Aucune police trouvée dans $folder"
        return
    }

    # Réinitialisation de l'interface
    $progress.Maximum = $total
    $progress.Value = 0
    $btnCancel.Enabled = $true
    $script:cancelRequested = $false
    $lblStatus.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['Installing']

    # Installation des polices
    $successCount = 0
    for ($i = 0; $i -lt $total; $i++) {
        if ($script:cancelRequested) { break }
        
        if (Test-FontFile -Font $FontFiles[$i] -and Install-Font -Font $FontFiles[$i]) {
            $successCount++
        }

        $progress.Value = $i + 1
        $lblStatus.Text = [string]::Format($script:TRANSLATIONS[$script:CurrentLanguage]['Processing'], $i+1, $total)
        [System.Windows.Forms.Application]::DoEvents()
    }

    # Finalisation
    $btnCancel.Enabled = $false
    if ($script:cancelRequested) {
        $lblStatus.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['Cancelled']
        Write-Log "Installation interrompue : $successCount/$total polices installées"
    } else {
        $lblStatus.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['Completed']
        Write-Log "Installation terminée : $successCount/$total polices installées"
        
        # Message de succès
        [System.Windows.Forms.MessageBox]::Show(
            [string]::Format($script:TRANSLATIONS[$script:CurrentLanguage]['SuccessMessage'], $successCount),
            "Succès",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information)
        
        # Fenêtre de redémarrage
        $restartForm = New-Object System.Windows.Forms.Form
        $restartForm.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['WindowTitle']
        $restartForm.Size = New-Object System.Drawing.Size(400, 200)
        $restartForm.StartPosition = 'CenterScreen'
        $restartForm.FormBorderStyle = 'FixedDialog'
        $restartForm.MaximizeBox = $false
        $restartForm.MinimizeBox = $false

        $label = New-Object System.Windows.Forms.Label
        $label.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['RestartMessage']
        $label.AutoSize = $true
        $label.Location = New-Object System.Drawing.Point(20, 20)
        $restartForm.Controls.Add($label)

        $btnRestartExplorer = New-Object System.Windows.Forms.Button
        $btnRestartExplorer.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['RestartExplorer']
        $btnRestartExplorer.Location = New-Object System.Drawing.Point(20, 100)
        $btnRestartExplorer.Size = New-Object System.Drawing.Size(150, 30)
        $btnRestartExplorer.Add_Click({
            Stop-Process -Name explorer -Force
            Start-Process explorer
            $restartForm.Close()
        })
        $restartForm.Controls.Add($btnRestartExplorer)

        $btnRestartPC = New-Object System.Windows.Forms.Button
        $btnRestartPC.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['RestartPC']
        $btnRestartPC.Location = New-Object System.Drawing.Point(190, 100)
        $btnRestartPC.Size = New-Object System.Drawing.Size(150, 30)
        $btnRestartPC.Add_Click({
            Restart-Computer -Force
        })
        $restartForm.Controls.Add($btnRestartPC)

        $btnCancelRestart = New-Object System.Windows.Forms.Button
        $btnCancelRestart.Text = $script:TRANSLATIONS[$script:CurrentLanguage]['Cancel']
        $btnCancelRestart.Location = New-Object System.Drawing.Point(20, 140)
        $btnCancelRestart.Size = New-Object System.Drawing.Size(320, 30)
        $btnCancelRestart.Add_Click({
            $restartForm.Close()
        })
        $restartForm.Controls.Add($btnCancelRestart)

        [void]$restartForm.ShowDialog()
    }
})
#endregion

# Après la création du formulaire
$form.Add_FormClosing({
    param($formSender, $e)
    Write-Log "Fermeture de l'application..."
    if ($btnCancel.Enabled) {
        $script:cancelRequested = $true
        Write-Log "Installation en cours annulée"
    }
    Save-UserPreferences
    # Nettoyage des ressources
    $progress.Dispose()
    $btnBrowse.Dispose()
    $btnCancel.Dispose()
    $comboLanguage.Dispose()
})

# Vérification des mises à jour au démarrage
Check-ForUpdates

# Application du thème initial
Apply-Theme $form

# Afficher la fenêtre
[void] $form.ShowDialog()

# Information finale
Write-Log "Application fermée. Logs disponibles: $script:logFile"
