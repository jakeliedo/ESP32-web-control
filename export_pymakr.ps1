# Pymakr Extension Export Script
# This script exports Pymakr extension to .vsix file

param(
    [string]$OutputPath = "B:\Python\MicroPython\ESP_WC_System\extensions",
    [string]$ExtensionId = "pycom.pymakr"
)

Write-Host "=== Pymakr Extension Export Tool ===" -ForegroundColor Green
Write-Host ""

# Create output directory if it doesn't exist
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force
    Write-Host "Created directory: $OutputPath" -ForegroundColor Yellow
}

# Get VS Code extensions directory
$vsCodeExtensionsPath = ""
$possiblePaths = @(
    "$env:USERPROFILE\.vscode\extensions",
    "$env:USERPROFILE\.vscode-insiders\extensions",
    "$env:APPDATA\Code\User\extensions"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $vsCodeExtensionsPath = $path
        break
    }
}

if ([string]::IsNullOrEmpty($vsCodeExtensionsPath)) {
    Write-Host "❌ Could not find VS Code extensions directory!" -ForegroundColor Red
    exit 1
}

Write-Host "VS Code extensions directory: $vsCodeExtensionsPath" -ForegroundColor Cyan

# Find Pymakr extension directory
$pymakrDirs = Get-ChildItem -Path $vsCodeExtensionsPath -Directory | Where-Object { $_.Name -like "*pymakr*" }

if ($pymakrDirs.Count -eq 0) {
    Write-Host "❌ Pymakr extension not found!" -ForegroundColor Red
    exit 1
}

Write-Host "`nFound Pymakr extensions:" -ForegroundColor Yellow
foreach ($dir in $pymakrDirs) {
    Write-Host "  - $($dir.Name)" -ForegroundColor White
}

# Let user choose which extension to export
if ($pymakrDirs.Count -gt 1) {
    Write-Host "`nWhich extension would you like to export?" -ForegroundColor Cyan
    for ($i = 0; $i -lt $pymakrDirs.Count; $i++) {
        Write-Host "  $($i + 1). $($pymakrDirs[$i].Name)" -ForegroundColor White
    }
    
    do {
        $choice = Read-Host "Enter choice (1-$($pymakrDirs.Count))"
        $choiceNum = [int]$choice - 1
    } while ($choiceNum -lt 0 -or $choiceNum -ge $pymakrDirs.Count)
    
    $selectedExtension = $pymakrDirs[$choiceNum]
} else {
    $selectedExtension = $pymakrDirs[0]
}

Write-Host "`nSelected extension: $($selectedExtension.Name)" -ForegroundColor Green

# Get extension info from package.json
$packageJsonPath = Join-Path $selectedExtension.FullName "package.json"
if (!(Test-Path $packageJsonPath)) {
    Write-Host "❌ package.json not found in extension directory!" -ForegroundColor Red
    exit 1
}

$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
$extensionName = $packageJson.name
$extensionVersion = $packageJson.version
$extensionPublisher = $packageJson.publisher

Write-Host "Extension info:" -ForegroundColor Yellow
Write-Host "  Name: $extensionName" -ForegroundColor White
Write-Host "  Version: $extensionVersion" -ForegroundColor White
Write-Host "  Publisher: $extensionPublisher" -ForegroundColor White

# Create .vsix filename
$vsixFileName = "$extensionPublisher.$extensionName-$extensionVersion.vsix"
$vsixPath = Join-Path $OutputPath $vsixFileName

Write-Host "`nCreating .vsix file..." -ForegroundColor Green

# Method 1: Try using vsce (if available)
try {
    $vsceAvailable = Get-Command vsce -ErrorAction SilentlyContinue
    if ($vsceAvailable) {
        Write-Host "Using vsce to package extension..." -ForegroundColor Cyan
        Set-Location $selectedExtension.FullName
        & vsce package --out $vsixPath
        
        if (Test-Path $vsixPath) {
            Write-Host "✅ Successfully created: $vsixPath" -ForegroundColor Green
            Write-Host "File size: $((Get-Item $vsixPath).Length / 1MB) MB" -ForegroundColor Cyan
            exit 0
        }
    }
} catch {
    Write-Host "vsce not available or failed" -ForegroundColor Yellow
}

# Method 2: Manual zip creation (fallback)
Write-Host "Creating manual package..." -ForegroundColor Cyan

# Copy extension directory to temp location
$tempDir = Join-Path $env:TEMP "pymakr_export_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $selectedExtension.FullName -Destination $tempDir -Recurse -Force

# Remove unnecessary files
$filesToRemove = @(
    "*.vsix",
    "node_modules",
    ".git",
    ".gitignore",
    "*.log",
    "*.tmp"
)

foreach ($pattern in $filesToRemove) {
    Get-ChildItem -Path $tempDir -Name $pattern -Recurse | ForEach-Object {
        $fullPath = Join-Path $tempDir $_
        if (Test-Path $fullPath) {
            Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# Create ZIP file (VS Code extension format)
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $vsixPath)
    
    # Rename to .vsix
    if (Test-Path $vsixPath) {
        Write-Host "✅ Successfully created: $vsixPath" -ForegroundColor Green
        Write-Host "File size: $((Get-Item $vsixPath).Length / 1MB) MB" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Failed to create .vsix file: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Clean up temp directory
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n=== Export Complete ===" -ForegroundColor Green
Write-Host "Output directory: $OutputPath" -ForegroundColor Cyan

# List all .vsix files in output directory
$vsixFiles = Get-ChildItem -Path $OutputPath -Filter "*.vsix"
if ($vsixFiles.Count -gt 0) {
    Write-Host "`nAvailable .vsix files:" -ForegroundColor Yellow
    foreach ($file in $vsixFiles) {
        Write-Host "  - $($file.Name) ($([math]::Round($file.Length / 1MB, 2)) MB)" -ForegroundColor White
    }
}

Write-Host "`nTo install the extension later, use:" -ForegroundColor Cyan
Write-Host "  code --install-extension `"$vsixPath`"" -ForegroundColor White
