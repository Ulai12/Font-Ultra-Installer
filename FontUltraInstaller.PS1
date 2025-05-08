# FontUltraInstaller.ps1
# Point d'entrée du programme
# Ce fichier charge la gestion des langues, le backend (Core) et le frontend (UI)

# Dictionnaire des traductions
$script:TRANSLATIONS = @{
    'fr' = @{
        'WindowTitle'      = "Installateur Ultra De Polices"
        'BrowseButton'     = "Parcourir..."
        'CancelButton'     = "Annuler"
        'NoFolderSelected' = "Aucun dossier sélectionné"
        'Ready'            = "Prêt."
        'Installing'       = "Installation en cours..."
        'Processing'       = "Traitement {0}/{1}"
        'Cancelled'        = "Installation annulée."
        'Completed'        = "Terminé!"
        'NoFontsFound'     = "Aucune police trouvée dans le dossier sélectionné."
        'AdminRequired'    = "Ce programme nécessite des droits administrateur."
        'SuccessMessage'   = "{0} polices ont été installées avec succès."
        'DevelopedBy'      = "Développé par {0} | Font Installer v{1}"
        'RestartMessage'   = "Pour que les nouvelles polices soient disponibles, vous devez redémarrer l'explorateur de fichiers ou votre PC."
        'RestartExplorer'  = "Redémarrer l'explorateur"
        'RestartPC'        = "Redémarrer le PC"
        'Cancel'           = "Annuler"
        'InstalledFonts'   = "Polices installées"
        'AlreadyInstalled' = "Déjà installées"
        'FailedFonts'      = "Échecs d'installation"
        'OpenFontsFolder'  = "Ouvrir le dossier des polices"
        'UpdateAvailable'  = "Une mise à jour est disponible (v{0})"
        'UpdateNow'        = "Mettre à jour maintenant"
        'UpdateLater'      = "Plus tard"
        'DragDropMessage'  = "Glissez-déposez vos polices ici"
        'ThemeLight'       = "Thème clair"
        'ThemeDark'        = "Thème sombre"
    }
    'en' = @{
        'WindowTitle'      = "Font Ultra Installer"
        'BrowseButton'     = "Browse..."
        'CancelButton'     = "Cancel"
        'NoFolderSelected' = "No folder selected"
        'Ready'            = "Ready."
        'Installing'       = "Installing..."
        'Processing'       = "Processing {0}/{1}"
        'Cancelled'        = "Installation cancelled."
        'Completed'        = "Completed!"
        'NoFontsFound'     = "No fonts found in selected folder."
        'AdminRequired'    = "This program requires administrator rights."
        'SuccessMessage'   = "{0} fonts have been successfully installed."
        'DevelopedBy'      = "Developed by {0} | Font Installer v{1}"
        'RestartMessage'   = "To make the new fonts available, you need to restart File Explorer or your PC."
        'RestartExplorer'  = "Restart Explorer"
        'RestartPC'        = "Restart PC"
        'Cancel'           = "Cancel"
        'InstalledFonts'   = "Installed fonts"
        'AlreadyInstalled' = "Already installed"
        'FailedFonts'      = "Installation failed"
        'OpenFontsFolder'  = "Open fonts folder"
        'UpdateAvailable'  = "An update is available (v{0})"
        'UpdateNow'        = "Update now"
        'UpdateLater'      = "Later"
        'DragDropMessage'  = "Drag and drop your fonts here"
        'ThemeLight'       = "Light theme"
        'ThemeDark'        = "Dark theme"
    }
}

# Détection de la langue du système et configuration de la langue par défaut
$script:CurrentLanguage = (Get-Culture).TwoLetterISOLanguageName
if (-not $script:TRANSLATIONS.ContainsKey($script:CurrentLanguage)) {
    $script:CurrentLanguage = 'en' # Langue par défaut si non supportée
}

# Fonction pour récupérer un texte traduit
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

# Contenu de FontUltraInstaller.Core.ps1
# Backend : logique métier

#region Configuration
# Constantes
$script:CONFIG = @{
    WindowTitle         = "Font Installer"
    WindowWidth         = 800
    WindowHeight        = 600
    Version             = "1.0.5"
    Author              = "JULAI GAVENOU"
    SupportedExtensions = @('.ttf', '.otf', '.fon', '.woff', '.woff2')
    UpdateCheckUrl      = "https://api.github.com/repos/Ulai12/Font-Ultra-Installer/releases/latest"
    Theme               = "Light" # Light ou Dark
    MaxFontSize         = 100MB # Taille maximale d'une police
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

function Test-FontFile {
    param(
        [System.IO.FileInfo]$Font
    )
    try {
        # Vérification de la taille du fichier
        if ($Font.Length -gt $script:CONFIG.MaxFontSize) {
            Write-Log "Police trop volumineuse: $($Font.Name) ($([math]::Round($Font.Length/1MB, 2)) MB)"
            return $false
        }

        # Vérification de l'extension
        if (-not ($script:CONFIG.SupportedExtensions -contains $Font.Extension.ToLower())) {
            Write-Log "Extension non supportée: $($Font.Extension)"
            return $false
        }

        # Vérification de la signature du fichier
        $stream = [System.IO.File]::OpenRead($Font.FullName)
        try {
            if ($Font.Extension -ieq '.ttf' -or $Font.Extension -ieq '.otf') {
                $buffer = New-Object byte[] 4
                $stream.Read($buffer, 0, 4) | Out-Null
                $signature = [System.Text.Encoding]::ASCII.GetString($buffer)
                return $signature -match '(OTTO|true|typ1)'
            }
            elseif ($Font.Extension -ieq '.woff' -or $Font.Extension -ieq '.woff2') {
                $buffer = New-Object byte[] 4
                $stream.Read($buffer, 0, 4) | Out-Null
                $signature = [System.Text.Encoding]::ASCII.GetString($buffer)
                return $signature -match 'wOFF'
            }
            return $true
        }
        finally {
            $stream.Close()
        }
    }
    catch {
        Write-Log "Erreur de validation pour $($Font.Name): $_"
        return $false
    }
}

function Install-Font {
    param(
        [System.IO.FileInfo]$Font,
        [System.Windows.Forms.ListView]$ListView
    )
    try {
        if (-not (Test-FontFile -Font $Font)) {
            Write-Log "Fichier police invalide: $($Font.Name)"
            $ListView.Items.Add([PSCustomObject]@{
                    Name   = $Font.Name
                    Status = "Échec"
                    Type   = $Font.Extension
                })
            return $false
        }
        
        $dest = Join-Path $env:WINDIR\Fonts $Font.Name
        if (-not (Test-Path $dest)) {
            # Vérification de l'espace disque disponible
            $drive = Get-PSDrive -PSProvider FileSystem | Where-Object { $env:WINDIR.StartsWith($_.Root) }
            if ($drive.Free -lt $Font.Length) {
                Write-Log "Espace disque insuffisant pour installer $($Font.Name)"
                $ListView.Items.Add([PSCustomObject]@{
                        Name   = $Font.Name
                        Status = "Échec (Espace insuffisant)"
                        Type   = $Font.Extension
                    })
                return $false
            }

            Copy-Item -Path $Font.FullName -Destination $dest -ErrorAction Stop
            $regName = switch ($Font.Extension.ToLower()) {
                '.otf' { "$($Font.BaseName) (OpenType)" }
                '.woff' { "$($Font.BaseName) (WOFF)" }
                '.woff2' { "$($Font.BaseName) (WOFF2)" }
                default { "$($Font.BaseName) (TrueType)" }
            }
    
            try {
                New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' `
                    -Name $regName -PropertyType String -Value $Font.Name -Force | Out-Null
                Write-Log "Installé: $($Font.Name)"
                $ListView.Items.Add([PSCustomObject]@{
                        Name   = $Font.Name
                        Status = "Installé"
                        Type   = $Font.Extension
                    })
                return $true
            }
            catch {
                # Nettoyage en cas d'échec de l'enregistrement
                if (Test-Path $dest) {
                    Remove-Item $dest -Force
                }
                throw
            }
        }
        Write-Log "Déjà installé: $($Font.Name)"
        $ListView.Items.Add([PSCustomObject]@{
                Name   = $Font.Name
                Status = "Déjà installé"
                Type   = $Font.Extension
            })
        return $true
    }
    catch {
        Write-Log "Erreur critique lors de l'installation de $($Font.Name): $_"
        $ListView.Items.Add([PSCustomObject]@{
                Name   = $Font.Name
                Status = "Échec"
                Type   = $Font.Extension
            })
        [System.Windows.Forms.MessageBox]::Show(
            "Erreur lors de l'installation de $($Font.Name)`n`nDétails: $_",
            "Erreur",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error)
        return $false
    }
}

function Write-Log {
    param([string]$message)
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $entry = "$timestamp - $message"
    Add-Content -Path $script:logFile -Value $entry
    Write-Host $entry
}

function Test-ForUpdates {
    try {
        $response = Invoke-RestMethod -Uri $script:CONFIG.UpdateCheckUrl -ErrorAction Stop
        $latestVersion = $response.tag_name.TrimStart('v')
        
        # Ne déclencher la mise à jour que si la version distante est strictement plus récente
        if ([version]$latestVersion -gt [version]$script:CONFIG.Version) {
            Write-Log "Nouvelle version disponible: $latestVersion (actuelle: $($script:CONFIG.Version))"
            return $latestVersion
        }
        return $null
    }
    catch {
        Write-Log "Erreur lors de la vérification des mises à jour: $_"
        return $null
    }
}

# Contenu de FontUltraInstaller.UI.ps1
# Interface graphique

# --- Fenêtre principale ---
$form = New-Object System.Windows.Forms.Form
$form.Text = Get-TranslatedText 'WindowTitle'
$form.Size = New-Object System.Drawing.Size($script:CONFIG.WindowWidth, $script:CONFIG.WindowHeight)
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.MinimizeBox = $true
$form.StartPosition = 'CenterScreen'
$form.Font = New-Object System.Drawing.Font('Segoe UI', 10)
$form.AllowDrop = $true

# --- Application du thème ---
function Set-Theme {
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

# --- En-tête (logo, titre, version, crédits, langue) ---
# Logo (utiliser l'icône)
$logo = New-Object System.Windows.Forms.PictureBox
$logo.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::StretchImage
$logo.Location = New-Object System.Drawing.Point(20, 10)
$logo.Size = New-Object System.Drawing.Size(60, 40)

# Vérifier si le fichier icône existe
$iconPath = "C:\Users\SHÔGUN\Downloads\ULTRA FONT INSTALLER\FontUltraInstaller.ico"
if (Test-Path $iconPath) {
    $logo.Image = [System.Drawing.Image]::FromFile($iconPath)
}
else {
    $logo.Image = [System.Drawing.SystemIcons]::Information.ToBitmap()
    Write-Log "Fichier icône introuvable : $iconPath"
}

$form.Controls.Add($logo)

# Titre
$title = New-Object System.Windows.Forms.Label
$title.Text = Get-TranslatedText 'WindowTitle'
$title.Font = New-Object System.Drawing.Font('Segoe UI', 16, [System.Drawing.FontStyle]::Bold)
$title.Location = New-Object System.Drawing.Point(90, 15)
$title.Size = New-Object System.Drawing.Size(350, 30)
$form.Controls.Add($title)

# Version et crédits
$credits = New-Object System.Windows.Forms.Label
$credits.Text = [string]::Format($(Get-TranslatedText 'DevelopedBy'), $script:CONFIG.Author, $script:CONFIG.Version)
$credits.Font = New-Object System.Drawing.Font('Segoe UI', 10)
$credits.Location = New-Object System.Drawing.Point(90, 45)
$credits.Size = New-Object System.Drawing.Size(350, 20)
$form.Controls.Add($credits)

# --- Séparateur visuel ---
$sep1 = New-Object System.Windows.Forms.Label
$sep1.BorderStyle = 'Fixed3D'
$sep1.AutoSize = $false
$sep1.Height = 2
$sep1.Width = 760
$sep1.Location = New-Object System.Drawing.Point(20, 70)
$form.Controls.Add($sep1)

# Label dossier
$lblFolder = New-Object System.Windows.Forms.Label
$lblFolder.Text = Get-TranslatedText 'NoFolderSelected'
$lblFolder.AutoSize = $true
$lblFolder.Location = New-Object System.Drawing.Point(20, 90)
$form.Controls.Add($lblFolder)

# Bouton Parcourir
$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = Get-TranslatedText 'BrowseButton'
$btnBrowse.Size = New-Object System.Drawing.Size(120, 30)
$btnBrowse.Location = New-Object System.Drawing.Point(660, 85)
$btnBrowse.FlatStyle = 'System'
$form.Controls.Add($btnBrowse)

# --- Séparateur visuel ---
$sep2 = New-Object System.Windows.Forms.Label
$sep2.BorderStyle = 'Fixed3D'
$sep2.AutoSize = $false
$sep2.Height = 2
$sep2.Width = 760
$sep2.Location = New-Object System.Drawing.Point(20, 120)
$form.Controls.Add($sep2)

# Barre de progression
$progress = New-Object System.Windows.Forms.ProgressBar
$progress.Location = New-Object System.Drawing.Point(20, 135)
$progress.Size = New-Object System.Drawing.Size(760, 25)
$progress.Style = 'Continuous'
$form.Controls.Add($progress)

# Label statut
$lblStatus = New-Object System.Windows.Forms.Label
$lblStatus.Text = Get-TranslatedText 'Ready'
$lblStatus.AutoSize = $true
$lblStatus.Location = New-Object System.Drawing.Point(20, 165)
$form.Controls.Add($lblStatus)

# --- Séparateur visuel ---
$sep3 = New-Object System.Windows.Forms.Label
$sep3.BorderStyle = 'Fixed3D'
$sep3.AutoSize = $false
$sep3.Height = 2
$sep3.Width = 760
$sep3.Location = New-Object System.Drawing.Point(20, 190)
$form.Controls.Add($sep3)

# Liste des polices installées
$listView = New-Object System.Windows.Forms.ListView
$listView.Location = New-Object System.Drawing.Point(20, 200)
$listView.Size = New-Object System.Drawing.Size(760, 300)
$listView.View = [System.Windows.Forms.View]::Details
$listView.FullRowSelect = $true
$listView.GridLines = $true
[void]$listView.Columns.Add($(Get-TranslatedText 'Name'), 350)
[void]$listView.Columns.Add($(Get-TranslatedText 'Status'), 150)
[void]$listView.Columns.Add($(Get-TranslatedText 'Type'), 100)
$form.Controls.Add($listView)

# --- Séparateur visuel ---
$sep4 = New-Object System.Windows.Forms.Label
$sep4.BorderStyle = 'Fixed3D'
$sep4.AutoSize = $false
$sep4.Height = 2
$sep4.Width = 760
$sep4.Location = New-Object System.Drawing.Point(20, 510)
$form.Controls.Add($sep4)

# Boutons d'action (version originale)
$btnInstall = New-Object System.Windows.Forms.Button
$btnInstall.Text = Get-TranslatedText 'InstallButton'
$btnInstall.Size = New-Object System.Drawing.Size(120, 35)
$btnInstall.Location = New-Object System.Drawing.Point(20, 520)
$btnInstall.FlatStyle = 'System'
$form.Controls.Add($btnInstall)

$btnCancel = New-Object System.Windows.Forms.Button
$btnCancel.Text = Get-TranslatedText 'CancelButton'
$btnCancel.Size = New-Object System.Drawing.Size(120, 35)
$btnCancel.Location = New-Object System.Drawing.Point(150, 520)
$btnCancel.Enabled = $false
$btnCancel.FlatStyle = 'System'
$form.Controls.Add($btnCancel)

$btnOpenFontsFolder = New-Object System.Windows.Forms.Button
$btnOpenFontsFolder.Text = Get-TranslatedText 'OpenFontsFolder'
$btnOpenFontsFolder.Size = New-Object System.Drawing.Size(200, 35)
$btnOpenFontsFolder.Location = New-Object System.Drawing.Point(280, 520)
$btnOpenFontsFolder.FlatStyle = 'System'
$form.Controls.Add($btnOpenFontsFolder)

# Bouton Paramètres fonctionnel
$btnSettings = New-Object System.Windows.Forms.Button
$btnSettings.Text = "Paramètres"
$btnSettings.Size = New-Object System.Drawing.Size(120, 35)
$btnSettings.Location = New-Object System.Drawing.Point(490, 520)
$btnSettings.FlatStyle = 'System'
$btnSettings.Add_Click({
        # Logique du bouton Paramètres
        $settingsForm = New-Object System.Windows.Forms.Form
        $settingsForm.Text = "Paramètres"
        $settingsForm.Size = New-Object System.Drawing.Size(400, 300)
    
        # Ajoutez ici les contrôles pour les paramètres
        $lblSettings = New-Object System.Windows.Forms.Label
        $lblSettings.Text = "Options de configuration"
        $lblSettings.Location = New-Object System.Drawing.Point(20, 20)
        $settingsForm.Controls.Add($lblSettings)
    
        [void]$settingsForm.ShowDialog()
    })
$form.Controls.Add($btnSettings)

# Bouton de changement de thème (rétabli)
$btnTheme = New-Object System.Windows.Forms.Button
$btnTheme.Text = if ($script:CONFIG.Theme -eq "Light") { Get-TranslatedText 'ThemeDark' } else { Get-TranslatedText 'ThemeLight' }
$btnTheme.Size = New-Object System.Drawing.Size(150, 35)
$btnTheme.Location = New-Object System.Drawing.Point(630, 520)
$btnTheme.FlatStyle = 'System'
$btnTheme.Add_Click({
        $script:CONFIG.Theme = if ($script:CONFIG.Theme -eq "Light") { "Dark" } else { "Light" }
        $btnTheme.Text = if ($script:CONFIG.Theme -eq "Light") { Get-TranslatedText 'ThemeDark' } else { Get-TranslatedText 'ThemeLight' }
        Set-Theme $form
    })
$form.Controls.Add($btnTheme)

# Sélecteur de langue (repositionné)
$comboLanguage = New-Object System.Windows.Forms.ComboBox
$comboLanguage.Location = New-Object System.Drawing.Point(620, 20)  # Nouvelle position
$comboLanguage.Size = New-Object System.Drawing.Size(70, 30)
$comboLanguage.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
$script:TRANSLATIONS.Keys | ForEach-Object { 
    [void]$comboLanguage.Items.Add($_) 
}
$comboLanguage.SelectedItem = $script:CurrentLanguage
$form.Controls.Add($comboLanguage)

#region Gestionnaires d'événements
# Gestion du changement de langue
$comboLanguage.Add_SelectedIndexChanged({
        $script:CurrentLanguage = $comboLanguage.SelectedItem
    
        # Mise à jour des textes de l'interface
        $form.Text = Get-TranslatedText 'WindowTitle'
        $title.Text = Get-TranslatedText 'WindowTitle'
        $credits.Text = [string]::Format($(Get-TranslatedText 'DevelopedBy'), $script:CONFIG.Author, $script:CONFIG.Version)
        $btnBrowse.Text = Get-TranslatedText 'BrowseButton'
        $btnCancel.Text = Get-TranslatedText 'CancelButton'
        $btnInstall.Text = Get-TranslatedText 'InstallButton'
        $btnOpenFontsFolder.Text = Get-TranslatedText 'OpenFontsFolder'
        $lblStatus.Text = Get-TranslatedText 'Ready'
        $listView.Columns[0].Text = Get-TranslatedText 'Name'
        $listView.Columns[1].Text = Get-TranslatedText 'Status'
        $listView.Columns[2].Text = Get-TranslatedText 'Type'
        $btnTheme.Text = if ($script:CONFIG.Theme -eq "Light") { Get-TranslatedText 'ThemeDark' } else { Get-TranslatedText 'ThemeLight' }
        
        if ($lblFolder.Text -eq $script:TRANSLATIONS['en']['NoFolderSelected'] -or 
            $lblFolder.Text -eq $script:TRANSLATIONS['fr']['NoFolderSelected']) {
            $lblFolder.Text = Get-TranslatedText 'NoFolderSelected'
        }
    })

# Changement de thème
$btnTheme.Add_Click({
        $script:CONFIG.Theme = if ($script:CONFIG.Theme -eq "Light") { "Dark" } else { "Light" }
        $btnTheme.Text = if ($script:CONFIG.Theme -eq "Light") { Get-TranslatedText 'ThemeDark' } else { Get-TranslatedText 'ThemeLight' }
        Set-Theme $form
    })

# Ouvrir dossier des polices
$btnOpenFontsFolder.Add_Click({
        Start-Process "explorer.exe" -ArgumentList "$env:WINDIR\Fonts"
    })

# Action Annuler
$btnCancel.Add_Click({
        $script:cancelRequested = $true
        Write-Log "Annulation demandée par l'utilisateur"
        $lblStatus.Text = Get-TranslatedText 'Cancelled'
    })

# Action Parcourir
$btnBrowse.Add_Click({
        $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        if ($dialog.ShowDialog() -ne 'OK') { return }
    
        $folder = $dialog.SelectedPath
        $lblFolder.Text = $folder
        Write-Log "Dossier sélectionné: $folder"

        # Recherche des polices avec pattern matching
        $FontFiles = Get-ChildItem -Path $folder -Include $script:CONFIG.SupportedExtensions -File -Recurse
        $total = $FontFiles.Count

        if ($total -eq 0) {
            [System.Windows.Forms.MessageBox]::Show(
                $(Get-TranslatedText 'NoFontsFound'),
                "Information",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Information)
            Write-Log "Aucune police trouvée dans $folder"
            return
        }
        
        # Continuez avec le reste de votre logique d'installation...
    })

# Action Installer
$btnInstall.Add_Click({
        if ($lblFolder.Text -eq $(Get-TranslatedText 'NoFolderSelected')) {
            [System.Windows.Forms.MessageBox]::Show(
                $(Get-TranslatedText 'NoFolderSelected'),
                "Information",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Information)
            return
        }

        $folder = $lblFolder.Text
        # Vider la liste
        $listView.Items.Clear()

        # Recherche des polices avec pattern matching
        $FontFiles = Get-ChildItem -Path $folder -Include $script:CONFIG.SupportedExtensions -File -Recurse
        $total = $FontFiles.Count

        if ($total -eq 0) {
            [System.Windows.Forms.MessageBox]::Show(
                $(Get-TranslatedText 'NoFontsFound'),
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
        $btnInstall.Enabled = $false
        $script:cancelRequested = $false
        $lblStatus.Text = Get-TranslatedText 'Installing'

        # Installation des polices
        $successCount = 0
        for ($i = 0; $i -lt $total; $i++) {
            if ($script:cancelRequested) { break }
        
            if (Install-Font -Font $FontFiles[$i] -ListView $listView) {
                $successCount++
            }

            $progress.Value = $i + 1
            $lblStatus.Text = [string]::Format($(Get-TranslatedText 'Processing'), $i + 1, $total)
            [System.Windows.Forms.Application]::DoEvents()
        }

        # Finalisation
        $btnCancel.Enabled = $false
        $btnInstall.Enabled = $true
        if ($script:cancelRequested) {
            $lblStatus.Text = Get-TranslatedText 'Cancelled'
            Write-Log "Installation interrompue : $successCount/$total polices installées"
        }
        else {
            $lblStatus.Text = Get-TranslatedText 'Completed'
            Write-Log "Installation terminée : $successCount/$total polices installées"
        
            # Message de succès
            [System.Windows.Forms.MessageBox]::Show(
                [string]::Format($(Get-TranslatedText 'SuccessMessage'), $successCount),
                "Succès",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Information)
        
            # Fenêtre de redémarrage
            $restartForm = New-Object System.Windows.Forms.Form
            $restartForm.Text = Get-TranslatedText 'WindowTitle'
            $restartForm.Size = New-Object System.Drawing.Size(400, 200)
            $restartForm.StartPosition = 'CenterScreen'
            $restartForm.FormBorderStyle = 'FixedDialog'
            $restartForm.MaximizeBox = $false
            $restartForm.MinimizeBox = $false

            $label = New-Object System.Windows.Forms.Label
            $label.Text = Get-TranslatedText 'RestartMessage'
            $label.AutoSize = $true
            $label.Location = New-Object System.Drawing.Point(20, 20)
            $restartForm.Controls.Add($label)

            $btnRestartExplorer = New-Object System.Windows.Forms.Button
            $btnRestartExplorer.Text = Get-TranslatedText 'RestartExplorer'
            $btnRestartExplorer.Location = New-Object System.Drawing.Point(20, 100)
            $btnRestartExplorer.Size = New-Object System.Drawing.Size(150, 30)
            $btnRestartExplorer.Add_Click({
                    Restart-Explorer
                    $restartForm.Close()
                })
            $restartForm.Controls.Add($btnRestartExplorer)

            $btnRestartPC = New-Object System.Windows.Forms.Button
            $btnRestartPC.Text = Get-TranslatedText 'RestartPC'
            $btnRestartPC.Location = New-Object System.Drawing.Point(190, 100)
            $btnRestartPC.Size = New-Object System.Drawing.Size(150, 30)
            $btnRestartPC.Add_Click({
                    Restart-Computer -Force
                })
            $restartForm.Controls.Add($btnRestartPC)

            $btnCancelRestart = New-Object System.Windows.Forms.Button
            $btnCancelRestart.Text = Get-TranslatedText 'Cancel'
            $btnCancelRestart.Location = New-Object System.Drawing.Point(20, 140)
            $btnCancelRestart.Size = New-Object System.Drawing.Size(320, 30)
            $btnCancelRestart.Add_Click({
                    $restartForm.Close()
                })
            $restartForm.Controls.Add($btnCancelRestart)

            [void]$restartForm.ShowDialog()
        }
    })

# Gestion du glisser-déposer
$form.Add_DragEnter({
        param($source, $e)
        if ($e.Data.GetDataPresent([Windows.Forms.DataFormats]::FileDrop)) {
            $files = $e.Data.GetData([Windows.Forms.DataFormats]::FileDrop)
            $validFiles = $files | Where-Object {
                $ext = [System.IO.Path]::GetExtension($_).ToLower()
                $script:CONFIG.SupportedExtensions -contains $ext
            }
            if ($validFiles.Count -gt 0) {
                $e.Effect = [Windows.Forms.DragDropEffects]::Copy
            }
        }
    })

$form.Add_DragDrop({
        param($source, $e)
        $files = $e.Data.GetData([Windows.Forms.DataFormats]::FileDrop)
        if ($files) {
            $folder = if ((Get-Item $files[0]) -is [System.IO.DirectoryInfo]) {
                $files[0]
            }
            else {
                Split-Path $files[0]
            }
            $lblFolder.Text = $folder
            # Déclencher l'installation
            $btnInstall.PerformClick()
        }
    })

# Fermeture de l'application
$form.Add_FormClosing({
        param($formSender, $e)
        Write-Log "Fermeture de l'application..."
        if ($btnCancel.Enabled) {
            $script:cancelRequested = $true
            Write-Log "Installation en cours annulée"
        }
    
        # Sauvegarde des préférences en arrière-plan
        $scriptBlock = {
            param($Language, $LastFolder, $LogFile)
      
            # Fonction de log locale
            function Write-LocalLog {
                param([string]$message)
                $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
                $entry = "$timestamp - $message"
                Add-Content -Path $LogFile -Value $entry
            }
      
            # Sauvegarde des préférences
            $prefPath = Join-Path $env:APPDATA "FontInstaller\preferences.json"
            $prefs = @{
                LastLanguage = $Language
                LastFolder   = $LastFolder
            }
      
            try {
                $prefDir = Split-Path $prefPath -Parent
                if (-not (Test-Path $prefDir)) {
                    New-Item -ItemType Directory -Path $prefDir -Force | Out-Null
                }
                $prefs | ConvertTo-Json | Set-Content $prefPath -Force
                Write-LocalLog "Préférences sauvegardées en arrière-plan"
            }
            catch {
                Write-LocalLog "Erreur lors de la sauvegarde des préférences: $_"
            }
        }
    
        # Démarrer un job PowerShell en arrière-plan
        Start-Job -ScriptBlock $scriptBlock -ArgumentList $script:CurrentLanguage, $lblFolder.Text, $script:logFile | Out-Null
    })
#endregion

# Vérification des mises à jour au démarrage
$latestVersion = Test-ForUpdates
if ($latestVersion) {
    $result = [System.Windows.Forms.MessageBox]::Show(
        [string]::Format($(Get-TranslatedText 'UpdateAvailable'), $latestVersion),
        "Mise à jour disponible",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Information
    )
    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        Start-Process $script:CONFIG.UpdateCheckUrl
    }
}

# Application du thème initial
Set-Theme $form

# Vérification des droits admin
if (-not (Test-AdminRights)) {
    [System.Windows.Forms.MessageBox]::Show(
        $(Get-TranslatedText 'AdminRequired'),
        "Erreur",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

# Afficher la fenêtre
[void] $form.ShowDialog()

# Information finale
Write-Log "Application fermée. Logs disponibles: $script:logFile"

# Renommage de la fonction pour utiliser un verbe approuvé
function Set-FluentButtonStyle($btn, $accentColor) {
    # ...existing code...
}

# Mise à jour des appels à la fonction
Set-FluentButtonStyle $btnBrowse $fluentAccent
Set-FluentButtonStyle $btnInstall $fluentAccent
Set-FluentButtonStyle $btnCancel ([System.Drawing.Color]::FromArgb(232,17,35))
Set-FluentButtonStyle $btnOpenFontsFolder ([System.Drawing.Color]::FromArgb(32, 32, 32))
Set-FluentButtonStyle $btnSettings ([System.Drawing.Color]::FromArgb(96, 96, 96))
Set-FluentButtonStyle $btnTheme ([System.Drawing.Color]::FromArgb(0, 153, 188))
