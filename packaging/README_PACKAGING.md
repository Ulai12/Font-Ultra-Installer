# MSIX Packaging Guide

## Prerequisites
1.  **Windows 10 SDK** (for `MakeAppx.exe` and `SignTool.exe`).
2.  **PyInstaller** (`pip install pyinstaller`).

## Steps

### 1. Build Executable
First, compile the Python application into a single executable.
```bash
cd "d:\ULTRA FONT INSTALLER"
pyinstaller --noconfirm --onedir --windowed --icon "FontUltraInstaller.ico" --name "UltraFontInstaller" --add-data "bin;bin" "src/main.py"
```

### 2. Prepare Layout
Run the preparation script to organize files.
```bash
packaging\prepare_layout.bat
```
*Note: You must manually copy the generated `dist\UltraFontInstaller\UltraFontInstaller.exe` (and internal folders) to `packaging\layout` if the script doesn't handle the PyInstaller output specifically.*

### 3. Create Package
Open a "Developer Command Prompt for VS" and run:
```bash
MakeAppx pack /d "d:\ULTRA FONT INSTALLER\packaging\layout" /p "d:\ULTRA FONT INSTALLER\UltraFontInstaller.msix"
```

### 4. Sign Package
You need a certificate to install the MSIX.
```bash
# Create Self-Signed Cert
New-SelfSignedCertificate -Type Custom -Subject "CN=UltraFontInstaller" -KeyUsage DigitalSignature -FriendlyName "UltraFontInstaller" -CertStoreLocation "Cert:\LocalMachine\My"

# Sign
SignTool sign /fd SHA256 /a /f <PathToPfx> /p <Password> "d:\ULTRA FONT INSTALLER\UltraFontInstaller.msix"
```
