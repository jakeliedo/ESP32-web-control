# Pymakr VSIX Creator - Improved Version
# This script creates a proper VSIX file for Pymakr extension

param(
    [string]$OutputPath = "B:\Python\MicroPython\ESP_WC_System\extensions",
    [switch]$Preview = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Pymakr VSIX Creator - Improved Version ===" -ForegroundColor Green
Write-Host ""

# Create output directory
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

Set-Location $OutputPath

# Find VS Code extensions directory
$vsCodePaths = @(
    "$env:USERPROFILE\.vscode\extensions",
    "$env:USERPROFILE\.vscode-insiders\extensions",
    "$env:APPDATA\Code\User\extensions"
)

$extensionsPath = $null
foreach ($path in $vsCodePaths) {
    if (Test-Path $path) {
        $extensionsPath = $path
        break
    }
}

if (!$extensionsPath) {
    Write-Host "❌ VS Code extensions directory not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Extensions directory: $extensionsPath" -ForegroundColor Cyan

# Find Pymakr extensions
$pattern = if ($Preview) { "*pymakr-preview*" } else { "*pymakr*" }
$pymakrDirs = Get-ChildItem -Path $extensionsPath -Directory | Where-Object { 
    $_.Name -like $pattern -and $_.Name -notlike "*preview*" 
}

if ($Preview) {
    $pymakrDirs = Get-ChildItem -Path $extensionsPath -Directory | Where-Object { 
        $_.Name -like "*pymakr-preview*" 
    }
}

if ($pymakrDirs.Count -eq 0) {
    Write-Host "❌ Pymakr extension not found!" -ForegroundColor Red
    exit 1
}

# Select extension
if ($pymakrDirs.Count -gt 1) {
    Write-Host "Found multiple extensions:" -ForegroundColor Yellow
    for ($i = 0; $i -lt $pymakrDirs.Count; $i++) {
        Write-Host "  $($i + 1). $($pymakrDirs[$i].Name)" -ForegroundColor White
    }
    
    do {
        $choice = Read-Host "Select extension (1-$($pymakrDirs.Count))"
        $index = [int]$choice - 1
    } while ($index -lt 0 -or $index -ge $pymakrDirs.Count)
    
    $selectedExt = $pymakrDirs[$index]
} else {
    $selectedExt = $pymakrDirs[0]
}

Write-Host "Selected: $($selectedExt.Name)" -ForegroundColor Green

# Read package.json
$packageJsonPath = Join-Path $selectedExt.FullName "package.json"
if (!(Test-Path $packageJsonPath)) {
    Write-Host "❌ package.json not found!" -ForegroundColor Red
    exit 1
}

$packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
$extName = $packageJson.name
$extVersion = $packageJson.version
$extPublisher = $packageJson.publisher
$extDisplayName = $packageJson.displayName

Write-Host "Extension Info:" -ForegroundColor Yellow
Write-Host "  Publisher: $extPublisher" -ForegroundColor White
Write-Host "  Name: $extName" -ForegroundColor White
Write-Host "  Display Name: $extDisplayName" -ForegroundColor White
Write-Host "  Version: $extVersion" -ForegroundColor White

# Create VSIX filename
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$vsixName = "$extPublisher.$extName-$extVersion-$timestamp.vsix"
$vsixPath = Join-Path $OutputPath $vsixName

Write-Host "`nCreating VSIX: $vsixName" -ForegroundColor Green

# Method 1: Try using vsce if available
try {
    $vsce = Get-Command vsce -ErrorAction SilentlyContinue
    if ($vsce) {
        Write-Host "Using vsce (VS Code Extension CLI)..." -ForegroundColor Cyan
        Push-Location $selectedExt.FullName
        try {
            & vsce package --out $vsixPath
            if (Test-Path $vsixPath) {
                Write-Host "✅ VSIX created successfully with vsce!" -ForegroundColor Green
                Pop-Location
                exit 0
            }
        } catch {
            Write-Host "vsce failed: $($_.Exception.Message)" -ForegroundColor Yellow
        } finally {
            Pop-Location
        }
    }
} catch {
    Write-Host "vsce not available" -ForegroundColor Yellow
}

# Method 2: Download from marketplace
Write-Host "Attempting to download from marketplace..." -ForegroundColor Cyan

$marketplaceUrl = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/$extPublisher/vsextensions/$extName/latest/vspackage"
$downloadPath = Join-Path $OutputPath "marketplace-$extName.vsix"

try {
    Write-Host "Downloading from: $marketplaceUrl" -ForegroundColor Gray
    Invoke-WebRequest -Uri $marketplaceUrl -OutFile $downloadPath -UseBasicParsing
    
    if (Test-Path $downloadPath) {
        $fileSize = (Get-Item $downloadPath).Length
        if ($fileSize -gt 1000) {  # At least 1KB
            Write-Host "✅ Downloaded from marketplace: $downloadPath" -ForegroundColor Green
            Write-Host "   Size: $([math]::Round($fileSize / 1MB, 2)) MB" -ForegroundColor Cyan
            
            # Test the downloaded VSIX
            Write-Host "Testing VSIX structure..." -ForegroundColor Yellow
            try {
                Add-Type -AssemblyName System.IO.Compression.FileSystem
                $zip = [System.IO.Compression.ZipFile]::OpenRead($downloadPath)
                
                $hasManifest = $zip.Entries | Where-Object { $_.FullName -eq "extension.vsixmanifest" }
                $hasPackageJson = $zip.Entries | Where-Object { $_.FullName -eq "extension/package.json" }
                $hasContentTypes = $zip.Entries | Where-Object { $_.FullName -eq "[Content_Types].xml" }
                
                $zip.Dispose()
                
                if ($hasManifest -and $hasPackageJson -and $hasContentTypes) {
                    Write-Host "✅ VSIX structure is valid!" -ForegroundColor Green
                    
                    # Rename to final name
                    if (Test-Path $vsixPath) {
                        Remove-Item $vsixPath -Force
                    }
                    Move-Item $downloadPath $vsixPath
                    
                    Write-Host "✅ Final VSIX: $vsixPath" -ForegroundColor Green
                    exit 0
                } else {
                    Write-Host "⚠️ VSIX structure incomplete" -ForegroundColor Yellow
                    Write-Host "   Manifest: $($null -ne $hasManifest)" -ForegroundColor Gray
                    Write-Host "   Package.json: $($null -ne $hasPackageJson)" -ForegroundColor Gray
                    Write-Host "   Content Types: $($null -ne $hasContentTypes)" -ForegroundColor Gray
                }
            } catch {
                Write-Host "⚠️ Could not validate VSIX structure: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 3: Create proper VSIX manually
Write-Host "Creating VSIX manually with proper structure..." -ForegroundColor Cyan

$tempDir = Join-Path $env:TEMP "vsix_creation_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    # Copy extension content to temp/extension/
    $extDir = Join-Path $tempDir "extension"
    Copy-Item -Path $selectedExt.FullName -Destination $extDir -Recurse -Force
    
    # Clean up unnecessary files
    $cleanupPatterns = @("*.vsix", "node_modules", ".git", "*.log", "*.tmp", ".vscode-test")
    foreach ($pattern in $cleanupPatterns) {
        Get-ChildItem -Path $extDir -Name $pattern -Recurse -Force | ForEach-Object {
            $fullPath = Join-Path $extDir $_
            if (Test-Path $fullPath) {
                Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
    
    # Create [Content_Types].xml
    $contentTypesXml = @"
<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="json" ContentType="application/json" />
    <Default Extension="vsixmanifest" ContentType="text/xml" />
    <Default Extension="js" ContentType="application/javascript" />
    <Default Extension="css" ContentType="text/css" />
    <Default Extension="html" ContentType="text/html" />
    <Default Extension="png" ContentType="image/png" />
    <Default Extension="jpg" ContentType="image/jpeg" />
    <Default Extension="gif" ContentType="image/gif" />
    <Default Extension="svg" ContentType="image/svg+xml" />
    <Default Extension="md" ContentType="text/markdown" />
    <Default Extension="txt" ContentType="text/plain" />
</Types>
"@
    
    $contentTypesPath = Join-Path $tempDir "[Content_Types].xml"
    Set-Content -Path $contentTypesPath -Value $contentTypesXml -Encoding UTF8
    
    # Create extension.vsixmanifest
    $manifestXml = @"
<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
    <Metadata>
        <Identity Id="$extName" Version="$extVersion" Language="en-US" Publisher="$extPublisher" />
        <DisplayName>$extDisplayName</DisplayName>
        <Description>$($packageJson.description)</Description>
        <Categories>Other</Categories>
        <Tags>micropython,pymakr,esp32,pycom</Tags>
    </Metadata>
    <Installation>
        <InstallationTarget Id="Microsoft.VisualStudio.Code" Version="[1.74.0,)" />
    </Installation>
    <Dependencies />
    <Assets>
        <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    </Assets>
</PackageManifest>
"@
    
    $manifestPath = Join-Path $tempDir "extension.vsixmanifest"
    Set-Content -Path $manifestPath -Value $manifestXml -Encoding UTF8
    
    # Create VSIX (ZIP file)
    Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    if (Test-Path $vsixPath) {
        Remove-Item $vsixPath -Force
    }
    
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $vsixPath)
    
    if (Test-Path $vsixPath) {
        $fileSize = (Get-Item $vsixPath).Length
        Write-Host "✅ VSIX created successfully!" -ForegroundColor Green
        Write-Host "   File: $vsixPath" -ForegroundColor Cyan
        Write-Host "   Size: $([math]::Round($fileSize / 1MB, 2)) MB" -ForegroundColor Cyan
        
        # Verify structure
        Write-Host "Verifying VSIX structure..." -ForegroundColor Yellow
        $zip = [System.IO.Compression.ZipFile]::OpenRead($vsixPath)
        $entries = $zip.Entries | Select-Object FullName
        $zip.Dispose()
        
        $requiredFiles = @("extension.vsixmanifest", "extension/package.json", "[Content_Types].xml")
        $allPresent = $true
        
        foreach ($required in $requiredFiles) {
            $found = $entries | Where-Object { $_.FullName -eq $required }
            if ($found) {
                Write-Host "   ✅ $required" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $required" -ForegroundColor Red
                $allPresent = $false
            }
        }
        
        if ($allPresent) {
            Write-Host "🎉 VSIX structure is complete and valid!" -ForegroundColor Green
        } else {
            Write-Host "⚠️ VSIX may have structure issues" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "❌ Failed to create VSIX: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Cleanup
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Get-ChildItem -Path $OutputPath -Filter "*.vsix" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "📦 $($_.Name) ($size MB)" -ForegroundColor White
}

Write-Host "`nTo install:" -ForegroundColor Yellow
Write-Host "  code --install-extension `"$vsixPath`"" -ForegroundColor Gray
