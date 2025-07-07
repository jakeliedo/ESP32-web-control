# WC Control System - Git Push Helper
# This script helps you commit and push changes to Git repository

$ErrorActionPreference = "Continue"
Set-Location "B:\Python\MicroPython\ESP_WC_System"

Write-Host "=== WC Control System - Git Push Helper ===" -ForegroundColor Green
Write-Host ""

# Show current status
Write-Host "Current branch: " -NoNewline -ForegroundColor Yellow
git branch --show-current

Write-Host "`nRepository status:" -ForegroundColor Yellow
git status --short

Write-Host "`nLast commit:" -ForegroundColor Yellow
git log --oneline -1

Write-Host "`n=== Choose Action ===" -ForegroundColor Cyan
Write-Host "1. Push existing commits (if any)"
Write-Host "2. Add all changes and commit with new message"
Write-Host "3. Just show detailed status"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`nPushing to remote repository..." -ForegroundColor Green
        git push origin Analytic-UI
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pushed!" -ForegroundColor Green
        } else {
            Write-Host "❌ Push failed. Check network or repository access." -ForegroundColor Red
        }
    }
    "2" {
        Write-Host "`nEnter your commit message:" -ForegroundColor Yellow
        $commitMessage = Read-Host "Message"
        
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = "Update ESP32 WC Control System - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            Write-Host "Using default message: $commitMessage" -ForegroundColor Yellow
        }
        
        Write-Host "`nAdding files..." -ForegroundColor Green
        git add .
        
        Write-Host "Committing..." -ForegroundColor Green
        git commit -m $commitMessage
        
        Write-Host "Pushing to remote..." -ForegroundColor Green
        git push origin Analytic-UI
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully committed and pushed!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push. Check for conflicts." -ForegroundColor Red
        }
    }
    "3" {
        Write-Host "`nDetailed Status:" -ForegroundColor Yellow
        git status
        Write-Host "`nRemote info:" -ForegroundColor Yellow
        git remote -v
        Write-Host "`nLast 3 commits:" -ForegroundColor Yellow
        git log --oneline -3
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    }
}

Write-Host "`n=== Final Status ===" -ForegroundColor Cyan
git status --short

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
