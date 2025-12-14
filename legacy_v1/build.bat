@echo off
REM Script de compilation Ultra Font Installer en .exe
REM Utilise PyInstaller pour créer un executable Windows

echo ===============================================
echo    ULTRA FONT INSTALLER - Build Script
echo ===============================================
echo.

REM Verifier si PyInstaller est installe
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installation de PyInstaller...
    pip install pyinstaller
)

REM Verifier les dependances
echo [INFO] Verification des dependances...
pip install PySide6 qfluentwidgets Pillow --quiet

REM Nettoyer les builds precedents
echo [INFO] Nettoyage des builds precedents...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Compiler avec PyInstaller
echo.
echo [BUILD] Compilation en cours...
echo.

pyinstaller UltraFontInstaller.spec --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo ===============================================
    echo    BUILD REUSSI !
    echo ===============================================
    echo.
    echo L'executable se trouve dans:
    echo   dist\Ultra Font Installer\Ultra Font Installer.exe
    echo.
    echo Pour creer un installateur unique, utilisez:
    echo   pyinstaller UltraFontInstaller.spec --onefile
    echo.
) else (
    echo.
    echo [ERREUR] La compilation a echoue.
    echo Verifiez les erreurs ci-dessus.
)

pause
