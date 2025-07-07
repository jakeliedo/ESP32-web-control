@echo off
cd /d "B:\Python\MicroPython\ESP_WC_System"
echo.
echo === WC Control System - Git Status ===
echo.
echo Current branch:
git branch --show-current
echo.
echo Current status:
git status
echo.
echo Last commit:
git log --oneline -1
echo.
echo === Options ===
echo 1. Push current commits to remote
echo 2. Add changes and commit with custom message
echo 3. Reset cache/db files and push
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Pushing to remote...
    git push origin Analytic-UI
) else if "%choice%"=="2" (
    echo.
    set /p msg="Enter commit message: "
    git add .
    git commit -m "%msg%"
    git push origin Analytic-UI
) else if "%choice%"=="3" (
    echo.
    echo Resetting temporary files...
    git reset HEAD PC_host/__pycache__/database.cpython-313.pyc
    git reset HEAD PC_host/data/wc_system.db
    git checkout -- PC_host/__pycache__/database.cpython-313.pyc
    git checkout -- PC_host/data/wc_system.db
    echo Pushing...
    git push origin Analytic-UI
)

echo.
echo Done!
pause
