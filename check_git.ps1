# Git Status Check Script
Set-Location "B:\Python\MicroPython\ESP_WC_System"
Write-Host "Current branch:"
git branch --show-current
Write-Host "`nGit status:"
git status --short
Write-Host "`nLast commit:"
git log --oneline -1
Write-Host "`nRemote status:"
git status --porcelain -b
