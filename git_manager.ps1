# Git Management Script
# This script will handle the current Git state

Set-Location "B:\Python\MicroPython\ESP_WC_System"

Write-Host "=== WC Control System - Git Management ===" -ForegroundColor Green
Write-Host ""

# Check current status
Write-Host "Current branch: " -NoNewline
git branch --show-current

Write-Host "`nCurrent status:"
git status --short

Write-Host "`nLast commit:"
git log --oneline -1

# Handle Python cache and database files
Write-Host "`n=== Handling temporary files ===" -ForegroundColor Yellow
Write-Host "Adding __pycache__ to .gitignore if not already there..."
if (!(Select-String -Path ".gitignore" -Pattern "__pycache__" -Quiet)) {
    Add-Content -Path ".gitignore" -Value "`n# Python cache files`n__pycache__/`n*.pyc`n*.pyo`n*.pyd"
    Write-Host "Added Python cache patterns to .gitignore"
}

Write-Host "Adding database files to .gitignore if not already there..."
if (!(Select-String -Path ".gitignore" -Pattern "\.db$" -Quiet)) {
    Add-Content -Path ".gitignore" -Value "`n# Database files`n*.db`ndata/*.db"
    Write-Host "Added database patterns to .gitignore"
}

# Reset cache and db files
Write-Host "`nResetting temporary files..."
git checkout HEAD -- "PC_host/__pycache__/database.cpython-313.pyc" 2>$null
git checkout HEAD -- "PC_host/data/wc_system.db" 2>$null

Write-Host "`nFinal status:"
git status --short

Write-Host "`n=== Available Actions ===" -ForegroundColor Cyan
Write-Host "1. Push current commits to remote"
Write-Host "2. Add remaining changes and commit"
Write-Host "3. Check remote status"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3) or press Enter to continue"

switch ($choice) {
    "1" {
        Write-Host "`nPushing to remote..." -ForegroundColor Green
        git push origin Analytic-UI
    }
    "2" {
        Write-Host "`nAdding and committing remaining changes..." -ForegroundColor Green
        $commitMsg = Read-Host "Enter commit message (or press Enter for default)"
        if ([string]::IsNullOrEmpty($commitMsg)) {
            $commitMsg = "Update: Clean up cache files and improve gitignore"
        }
        git add .
        git commit -m $commitMsg
        git push origin Analytic-UI
    }
    "3" {
        Write-Host "`nChecking remote status..." -ForegroundColor Green
        git remote -v
        git log --oneline -5
    }
    default {
        Write-Host "No action taken."
    }
}

Write-Host "`nScript completed!" -ForegroundColor Green
