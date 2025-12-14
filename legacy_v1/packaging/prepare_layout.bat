@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
set "PACKAGE_DIR=%~dp0layout"

echo Cleaning previous build...
if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\assets"
mkdir "%PACKAGE_DIR%\bin"
mkdir "%PACKAGE_DIR%\src"

echo Copying Application Files...
copy "%PROJECT_ROOT%\start.bat" "%PACKAGE_DIR%\"
xcopy "%PROJECT_ROOT%\bin" "%PACKAGE_DIR%\bin" /E /I /Y
xcopy "%PROJECT_ROOT%\src" "%PACKAGE_DIR%\src" /E /I /Y
copy "%PROJECT_ROOT%\packaging\AppxManifest.xml" "%PACKAGE_DIR%\"

echo Copying Assets...
:: In a real scenario, we would generate these from the .ico
:: For now, we assume they exist or we copy placeholders if we had them.
:: We will just copy the ico as a placeholder for the user to convert.
copy "%PROJECT_ROOT%\FontUltraInstaller.ico" "%PACKAGE_DIR%\assets\app_icon.ico"

echo.
echo Packaging Layout Created at: %PACKAGE_DIR%
echo.
echo NEXT STEPS:
echo 1. You need to compile the Python app to an EXE (e.g. using PyInstaller) named 'UltraFontInstaller.exe'
echo    and place it in the root of the layout folder.
echo    OR update AppxManifest.xml to point to a launcher script (but EXE is preferred for Store).
echo 2. Generate the required PNG assets in the 'assets' folder.
echo 3. Run 'MakeAppx pack /d layout /p UltraFontInstaller.msix'
echo 4. Sign the package with 'SignTool'.
echo.
pause
