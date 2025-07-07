# Alternative method to create proper VSIX using VS Code CLI
# This method downloads extension directly from marketplace

param(
    [string]$OutputPath = "B:\Python\MicroPython\ESP_WC_System\extensions"
)

Write-Host "=== Alternative VSIX Download Method ===" -ForegroundColor Green

# Create output directory
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force
}

Set-Location $OutputPath

# Method 1: Download from VS Code Marketplace
Write-Host "`nDownloading Pymakr from VS Code Marketplace..." -ForegroundColor Cyan

try {
    # Pymakr stable version
    $url1 = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Pycom/vsextensions/pymakr/latest/vspackage"
    Invoke-WebRequest -Uri $url1 -OutFile "Pycom.pymakr-latest.vsix"
    
    if (Test-Path "Pycom.pymakr-latest.vsix") {
        $size = [math]::Round((Get-Item "Pycom.pymakr-latest.vsix").Length / 1MB, 2)
        Write-Host "✅ Downloaded Pymakr stable: $size MB" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to download stable version: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    # Pymakr preview version  
    $url2 = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Pycom/vsextensions/pymakr-preview/latest/vspackage"
    Invoke-WebRequest -Uri $url2 -OutFile "Pycom.pymakr-preview-latest.vsix"
    
    if (Test-Path "Pycom.pymakr-preview-latest.vsix") {
        $size = [math]::Round((Get-Item "Pycom.pymakr-preview-latest.vsix").Length / 1MB, 2)
        Write-Host "✅ Downloaded Pymakr preview: $size MB" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Failed to download preview version: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 2: Use VS Code extensions manager
Write-Host "`nUsing VS Code extensions manager..." -ForegroundColor Cyan

try {
    # Get installed extension info
    $extensions = code --list-extensions --show-versions | Select-String "pymakr"
    
    foreach ($ext in $extensions) {
        $extInfo = $ext.ToString().Split("@")
        $extId = $extInfo[0]
        $extVersion = $extInfo[1]
        
        Write-Host "Found: $extId version $extVersion" -ForegroundColor Yellow
        
        # Try to reinstall to get fresh copy
        Write-Host "Reinstalling $extId..." -ForegroundColor Cyan
        code --uninstall-extension $extId
        code --install-extension $extId
    }
} catch {
    Write-Host "❌ VS Code method failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Results ===" -ForegroundColor Green
Get-ChildItem -Path $OutputPath -Filter "*.vsix" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "📦 $($_.Name) - $size MB" -ForegroundColor White
}

Write-Host "`nTo test installation:" -ForegroundColor Cyan
Write-Host "code --install-extension `"path\to\file.vsix`"" -ForegroundColor White
