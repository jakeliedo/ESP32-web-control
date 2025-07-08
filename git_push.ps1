# Simple Git Push Script for WC Control System (PowerShell)
Write-Host "=== WC Control System - Git Push Helper (PowerShell) ===" -ForegroundColor Cyan

# Navigate to project directory
Set-Location -Path "B:\Python\MicroPython\ESP_WC_System"

# Show current status
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch"
Write-Host ""
Write-Host "Repository status:"
git status --short
Write-Host ""

# Show last commit
Write-Host "Last commit:"
git log --oneline -1
Write-Host ""

# Options for user
Write-Host "Choose an action:"
Write-Host "1. Push existing commits to remote (recommended)"
Write-Host "2. Add all changes and commit with new message"
Write-Host "3. Reset cache files and push clean"
Write-Host "4. Check what files are ready to commit"
Write-Host ""
$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    1 {
        Write-Host "\nPushing existing commits to remote repository..."
        git push origin Analytic-UI
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pushed to remote!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push. Check your network connection and repository access." -ForegroundColor Red
        }
    }
    2 {
        Write-Host ""
        $commit_msg = Read-Host "Enter your commit message"
        if ([string]::IsNullOrWhiteSpace($commit_msg)) {
            $commit_msg = "Update ESP32 WC Control System - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        }
        git add .
        git commit -m "$commit_msg"
        git push origin Analytic-UI
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully committed and pushed!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push. Check for conflicts or network issues." -ForegroundColor Red
        }
    }
    3 {
        Write-Host "\nResetting cache and database files..."
        git reset HEAD PC_host\__pycache__\* 2>$null
        git reset HEAD PC_host\data\*.db 2>$null
        git checkout -- PC_host\__pycache__\* 2>$null
        git checkout -- PC_host\data\*.db 2>$null
        Write-Host "Pushing clean repository..."
        git push origin Analytic-UI
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pushed clean repository!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push." -ForegroundColor Red
        }
    }
    4 {
        Write-Host "\nFiles staged for commit:"
        git diff --cached --name-only
        Write-Host "\nFiles modified but not staged:"
        git diff --name-only
        Write-Host "\nUntracked files:"
        git ls-files --others --exclude-standard
    }
    Default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Yellow
    }
}

Write-Host "\n=== Final Status ==="
git status --short
