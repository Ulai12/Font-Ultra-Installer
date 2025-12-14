# Script pour créer une release GitHub v2.0

$releaseBody = @"
## 🚀 Ultra Font Installer v2.0 - Rust Edition

### ✨ What's New in v2.0

#### Architecture Improvements
- **Hybrid Rust/Python Architecture**: Core font validation and metadata extraction now powered by Rust for maximum performance and safety
- **WebAssembly-Ready**: Rust components (font_tool.exe) provide a foundation for future cross-platform expansion
- **Advanced Font Analysis**: Using ttf-parser crate for deep font metadata extraction

#### New Features
- **8 Advanced Navigation Pages**: Home, Library, Google Fonts Store, Glyph Inspector, Typewriter, Font Versus, Settings, About
- **Drag-and-Drop Installation**: Intuitive interface with real-time font validation
- **Multi-Language Support**: Full English and French localization

#### UI/UX Enhancements
- **Glassmorphism Design**: Modern liquid glass aesthetic with transparency and blur effects
- **Animated Backgrounds**: Smooth opacity animations for dynamic visual experience
- **Fluent Widgets Integration**: Microsoft Fluent Design System for Windows 11 compatibility
- **Dark Mode Support**: Automatic theme detection with custom color palette
- **Advanced Font Cards**: Rich UI components with hover effects and context menus

#### Performance & Reliability
- **QThread Worker System**: All I/O operations run asynchronously to prevent UI blocking
- **Real-Time Progress Tracking**: Visual progress indicators for installations and downloads
- **Advanced Font Validation**: Multi-level validation system
- **System Integration**: PowerShell registry operations for persistent font installation

### 📋 Major Improvements vs v1.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Installation | ✅ | ✅ Enhanced with real-time validation |
| UI | ✅ Basic | ✅ Modern Glassmorphism + Fluent Widgets |
| TTF/OTF Support | ✅ | ✅ + WOFF, TTC, advanced metadata |
| Rust Integration | ❌ | ✅ Font validation & analysis |
| Multi-Page App | ❌ | ✅ 8 specialized pages |
| Font Preview | ❌ | ✅ Live previews |
| Font Comparison | ❌ | ✅ Side-by-side Versus page |
| Glyph Inspector | ❌ | ✅ Advanced character analysis |
| Google Fonts Store | ❌ | ✅ Direct integration |
| Localization | ❌ | ✅ FR/EN with auto-detect |

### 🛠️ Technical Details
- **Framework**: PySide6 with Fluent Widgets
- **Backend**: Rust (ttf-parser, serde)
- **System Integration**: PowerShell 5.1
- **Requirements**: Python 3.x, Rust (optional for building)

### 📦 Installation
1. Run `start.bat`
2. Dependencies auto-install (PySide6, Fluent Widgets, Pillow, packaging)
3. Optional: Rebuild Rust component with `cd src/rust && .\build.ps1`

---
**Build Date**: November 26, 2025
**Repository**: https://github.com/Ulai12/Font-Ultra-Installer
"@

# Créer le JSON pour la release
$releaseJson = @{
    tag_name    = "v2.0"
    name        = "v2.0 - Rust Edition with Advanced Features"
    body        = $releaseBody
    draft       = $false
    prerelease  = $false
} | ConvertTo-Json -Depth 10 -Compress

Write-Host "Release JSON prêt:" -ForegroundColor Green
Write-Host $releaseJson

# Vous devez avoir votre GitHub token dans une variable d'environnement
# ou le passer en paramètre
$githubToken = $env:GITHUB_TOKEN
if (-not $githubToken) {
    Write-Host "GITHUB_TOKEN non trouvé. Définissez-le comme variable d'environnement." -ForegroundColor Red
    exit 1
}

# Créer les headers pour l'API GitHub
$headers = @{
    "Authorization" = "token $githubToken"
    "Accept"        = "application/vnd.github.v3+json"
}

# Créer la release
Write-Host "Création de la release v2.0..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod `
        -Uri "https://api.github.com/repos/Ulai12/Font-Ultra-Installer/releases" `
        -Method Post `
        -Headers $headers `
        -Body $releaseJson `
        -ContentType "application/json"

    Write-Host "✅ Release créée avec succès!" -ForegroundColor Green
    Write-Host "URL: $($response.html_url)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Erreur lors de la création de la release:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
