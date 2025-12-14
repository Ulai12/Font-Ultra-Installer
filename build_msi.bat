@echo off
REM ============================================
REM Ultra Font Installer - Script de Build MSI
REM ============================================
REM Auteur: JULAI
REM Ce script compile l'application et génère l'installateur MSI
REM
REM Prérequis:
REM   1. Python avec les dépendances installées
REM   2. PyInstaller (pip install pyinstaller)
REM   3. WiX Toolset v4+ (winget install WixToolset.WixToolset)
REM      ou télécharger depuis: https://wixtoolset.org/
REM ============================================

echo.
echo ========================================
echo   Ultra Font Installer - Build MSI
echo ========================================
echo.

REM Vérifier si WiX est installé
where wix >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] WiX Toolset n'est pas installe ou n'est pas dans le PATH.
    echo.
    echo Pour installer WiX Toolset:
    echo   1. Via winget: winget install WixToolset.WixToolset
    echo   2. Ou telecharger depuis: https://wixtoolset.org/
    echo.
    pause
    exit /b 1
)

REM Étape 1: Compiler l'exécutable avec PyInstaller
echo [1/3] Compilation de l'executable avec PyInstaller...
echo.
pyinstaller "Ultra Font Installer.spec" --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] La compilation PyInstaller a echoue.
    pause
    exit /b 1
)
echo [OK] Executable compile avec succes.
echo.

REM Vérifier que l'exécutable existe
if not exist "dist\Ultra Font Installer.exe" (
    echo [ERREUR] L'executable n'a pas ete trouve dans dist\
    pause
    exit /b 1
)

REM Vérifier que l'icône existe
if not exist "FontUltraInstaller.ico" (
    echo [AVERTISSEMENT] FontUltraInstaller.ico non trouve.
    echo L'icone est necessaire pour l'installateur MSI.
    echo.
    echo.
)

REM Étape 2: Compiler le MSI avec WiX
echo [2/3] Generation du package MSI avec WiX Toolset...
echo.
wix build installer.wxs -o "dist\Ultra_Font_Installer_Setup_v2.0.0.msi" -ext WixToolset.UI.wixext
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] La generation du MSI a echoue.
    echo.
    echo Assurez-vous que WiX Toolset est correctement installe.
    pause
    exit /b 1
)
echo [OK] Package MSI genere avec succes.
echo.

REM Étape 3: Afficher le résumé
echo [3/3] Resume de la compilation:
echo.
echo ========================================
echo   Fichiers generes:
echo ========================================
echo   - dist\Ultra Font Installer.exe
echo   - dist\Ultra_Font_Installer_Setup_v2.0.0.msi
echo ========================================
echo.

REM Ouvrir le dossier dist
echo Ouverture du dossier de sortie...
explorer dist

echo.
echo [TERMINE] La compilation est terminee avec succes !
echo.
pause
