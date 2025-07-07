@echo off
echo === Pymakr Extension Export Tool ===
echo.

:: Create extensions directory
if not exist "B:\Python\MicroPython\ESP_WC_System\extensions" (
    mkdir "B:\Python\MicroPython\ESP_WC_System\extensions"
    echo Created extensions directory
)

cd /d "B:\Python\MicroPython\ESP_WC_System\extensions"

echo Current Pymakr extensions:
code --list-extensions | findstr -i pymakr

echo.
echo Available methods:
echo 1. Export using VS Code Extensions Manager
echo 2. Copy from extensions directory
echo 3. Download from marketplace
echo.

set /p choice="Choose method (1-3): "

if "%choice%"=="1" goto method1
if "%choice%"=="2" goto method2
if "%choice%"=="3" goto method3
goto end

:method1
echo.
echo Method 1: Using VS Code Extensions Manager...
echo Opening VS Code Extensions view...
code --list-extensions --show-versions | findstr -i pymakr
echo.
echo To export manually:
echo 1. Open VS Code
echo 2. Go to Extensions (Ctrl+Shift+X)
echo 3. Find Pymakr extension
echo 4. Click gear icon → "Copy Extension ID"
echo 5. Use: code --install-extension [extension-id] --force
goto end

:method2
echo.
echo Method 2: Copy from extensions directory...
powershell -ExecutionPolicy Bypass -File "export_pymakr.ps1"
goto end

:method3
echo.
echo Method 3: Download from marketplace...
echo Downloading Pymakr extension...
:: Download latest version
curl -L -o "pycom.pymakr.vsix" "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/pycom/vsextensions/pymakr/latest/vspackage"
if exist "pycom.pymakr.vsix" (
    echo ✅ Downloaded: pycom.pymakr.vsix
) else (
    echo ❌ Download failed
)
goto end

:end
echo.
echo Files in extensions directory:
dir *.vsix 2>nul
echo.
echo Export complete!
pause
