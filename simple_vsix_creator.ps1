# Simple Pymakr VSIX Creator
# Creates VSIX file for Pymakr extension with correct structure

$ErrorActionPreference = "Continue"

Write-Host "=== Simple Pymakr VSIX Creator ===" -ForegroundColor Green

$outputDir = "B:\Python\MicroPython\ESP_WC_System\extensions"
Set-Location $outputDir

# Method 1: Try downloading the latest from marketplace
Write-Host "Method 1: Downloading from VS Code Marketplace..." -ForegroundColor Cyan

$urls = @(
    @{
        Name = "Pycom.pymakr-stable"
        Url = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Pycom/vsextensions/pymakr/latest/vspackage"
    },
    @{
        Name = "Pycom.pymakr-preview"
        Url = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/Pycom/vsextensions/pymakr-preview/latest/vspackage"
    }
)

foreach ($item in $urls) {
    $fileName = "$($item.Name).vsix"
    Write-Host "Downloading $fileName..." -ForegroundColor Yellow
    
    try {
        Invoke-WebRequest -Uri $item.Url -OutFile $fileName -UseBasicParsing -TimeoutSec 30
        
        if (Test-Path $fileName) {
            $size = (Get-Item $fileName).Length
            if ($size -gt 1000000) {  # At least 1MB
                Write-Host "✅ Downloaded: $fileName ($([math]::Round($size/1MB,2)) MB)" -ForegroundColor Green
            } else {
                Write-Host "⚠️ File too small, may be error page" -ForegroundColor Yellow
                Remove-Item $fileName -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Method 2: Create from local extension using proper ZIP structure
Write-Host "`nMethod 2: Creating from local extension..." -ForegroundColor Cyan

$extensionsPath = "$env:USERPROFILE\.vscode\extensions"
$pymakrDir = Get-ChildItem -Path $extensionsPath -Directory | Where-Object { $_.Name -like "*pymakr*" -and $_.Name -notlike "*preview*" } | Select-Object -First 1

if ($pymakrDir) {
    Write-Host "Found local extension: $($pymakrDir.Name)" -ForegroundColor Yellow
    
    $packageJsonPath = Join-Path $pymakrDir.FullName "package.json"
    if (Test-Path $packageJsonPath) {
        try {
            $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
            $version = $packageJson.version
            $publisher = $packageJson.publisher
            $name = $packageJson.name
            
            $localVsixName = "$publisher.$name-$version-local.vsix"
            
            Write-Host "Creating $localVsixName..." -ForegroundColor Yellow
            
            # Create temporary directory with proper structure
            $tempDir = Join-Path $env:TEMP "pymakr_vsix_$(Get-Date -Format 'yyyyMMddHHmmss')"
            New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
            
            # Create extension subdirectory
            $extSubDir = Join-Path $tempDir "extension"
            Copy-Item -Path $pymakrDir.FullName -Destination $extSubDir -Recurse -Force
            
            # Remove unnecessary files
            $filesToRemove = @("*.vsix", "node_modules", ".git*", "*.log", ".vscode-test")
            foreach ($pattern in $filesToRemove) {
                Get-ChildItem -Path $extSubDir -Filter $pattern -Recurse -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            }
            
            # Create manifest file
            $manifestContent = @"
<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
    <Metadata>
        <Identity Id="$name" Version="$version" Language="en-US" Publisher="$publisher" />
        <DisplayName>Pymakr</DisplayName>
        <Description>Pymakr extension for MicroPython development</Description>
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
            Set-Content -Path (Join-Path $tempDir "extension.vsixmanifest") -Value $manifestContent -Encoding UTF8
            
            # Create content types file
            $contentTypesContent = @"
<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="json" ContentType="application/json" />
    <Default Extension="vsixmanifest" ContentType="text/xml" />
</Types>
"@
            Set-Content -Path (Join-Path $tempDir "[Content_Types].xml") -Value $contentTypesContent -Encoding UTF8
            
            # Create ZIP file
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            $zipPath = Join-Path $outputDir $localVsixName
            
            if (Test-Path $zipPath) {
                Remove-Item $zipPath -Force
            }
            
            [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $zipPath)
            
            # Clean up
            Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            
            if (Test-Path $zipPath) {
                $size = (Get-Item $zipPath).Length
                Write-Host "✅ Created: $localVsixName ($([math]::Round($size/1MB,2)) MB)" -ForegroundColor Green
            }
            
        } catch {
            Write-Host "❌ Failed to create local VSIX: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Summary
Write-Host "`n=== Available VSIX Files ===" -ForegroundColor Green
Get-ChildItem -Path $outputDir -Filter "*.vsix" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    $date = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    Write-Host "📦 $($_.Name)" -ForegroundColor White
    Write-Host "   Size: $size MB | Created: $date" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "To install any of these extensions:" -ForegroundColor Yellow
Write-Host "code --install-extension `"path\to\file.vsix`"" -ForegroundColor Gray
