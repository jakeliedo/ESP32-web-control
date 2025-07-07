# Fixed Pymakr Extension Export Script
# This script properly exports Pymakr extension to .vsix file with correct structure

param(
    [string]$OutputPath = "B:\Python\MicroPython\ESP_WC_System\extensions",
    [string]$ExtensionChoice = ""
)

Write-Host "=== Pymakr Extension Export Tool (Fixed) ===" -ForegroundColor Green
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
if ([string]::IsNullOrEmpty($ExtensionChoice)) {
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
} else {
    $choiceNum = [int]$ExtensionChoice - 1
    $selectedExtension = $pymakrDirs[$choiceNum]
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

Write-Host "`nCreating proper .vsix file..." -ForegroundColor Green

# Method 1: Try using vsce if available
try {
    $vsceCheck = & where.exe vsce 2>$null
    if ($vsceCheck) {
        Write-Host "Using vsce to package extension..." -ForegroundColor Cyan
        Set-Location $selectedExtension.FullName
        & vsce package --out $vsixPath
        
        if (Test-Path $vsixPath) {
            Write-Host "✅ Successfully created with vsce: $vsixPath" -ForegroundColor Green
            Write-Host "File size: $([math]::Round((Get-Item $vsixPath).Length / 1MB, 2)) MB" -ForegroundColor Cyan
            exit 0
        }
    }
} catch {
    Write-Host "vsce not available, using manual method..." -ForegroundColor Yellow
}

# Method 2: Create proper VSIX structure manually
Write-Host "Creating VSIX with proper structure..." -ForegroundColor Cyan

# Create temp directory with proper structure
$tempDir = Join-Path $env:TEMP "vsix_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$extensionDir = Join-Path $tempDir "extension"

# Create directory structure
New-Item -ItemType Directory -Path $extensionDir -Force | Out-Null

# Copy extension files to proper location
Copy-Item -Path "$($selectedExtension.FullName)\*" -Destination $extensionDir -Recurse -Force

# Remove unnecessary files from extension directory
$filesToRemove = @(
    "node_modules",
    ".git",
    ".gitignore", 
    "*.log",
    "*.tmp",
    ".vscode",
    "tsconfig.json",
    "webpack.config.js"
)

foreach ($pattern in $filesToRemove) {
    Get-ChildItem -Path $extensionDir -Name $pattern -Recurse -Force | ForEach-Object {
        $fullPath = Join-Path $extensionDir $_
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
</Types>
"@

$contentTypesPath = Join-Path $tempDir "[Content_Types].xml"
Set-Content -Path $contentTypesPath -Value $contentTypesXml -Encoding UTF8

# Create extension.vsixmanifest
$vsixManifest = @"
<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="$extensionName" Version="$extensionVersion" Publisher="$extensionPublisher" />
    <DisplayName>$($packageJson.displayName)</DisplayName>
    <Description xml:space="preserve">$($packageJson.description)</Description>
    <Tags>$($packageJson.keywords -join ",")</Tags>
    <Categories>$($packageJson.categories -join ",")</Categories>
    <GalleryFlags>Preview</GalleryFlags>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="$($packageJson.engines.vscode)" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.LocalizedLanguages" Value="" />
    </Properties>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"@

$manifestPath = Join-Path $tempDir "extension.vsixmanifest"
Set-Content -Path $manifestPath -Value $vsixManifest -Encoding UTF8

# Verify package.json exists in extension directory
$extPackageJsonPath = Join-Path $extensionDir "package.json"
if (!(Test-Path $extPackageJsonPath)) {
    Write-Host "❌ package.json missing from extension directory!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Extension structure verified" -ForegroundColor Green
Write-Host "  - [Content_Types].xml: $(Test-Path $contentTypesPath)" -ForegroundColor White
Write-Host "  - extension.vsixmanifest: $(Test-Path $manifestPath)" -ForegroundColor White  
Write-Host "  - extension/package.json: $(Test-Path $extPackageJsonPath)" -ForegroundColor White

# Create ZIP file with proper VSIX structure
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    
    # Remove existing file if it exists
    if (Test-Path $vsixPath) {
        Remove-Item $vsixPath -Force
    }
    
    # Create ZIP
    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, $vsixPath)
    
    if (Test-Path $vsixPath) {
        $fileSize = [math]::Round((Get-Item $vsixPath).Length / 1MB, 2)
        Write-Host "✅ Successfully created: $vsixPath" -ForegroundColor Green
        Write-Host "File size: $fileSize MB" -ForegroundColor Cyan
        
        # Verify VSIX structure
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $zipArchive = [System.IO.Compression.ZipFile]::OpenRead($vsixPath)
        $hasManifest = $zipArchive.Entries | Where-Object { $_.FullName -eq "extension.vsixmanifest" }
        $hasPackageJson = $zipArchive.Entries | Where-Object { $_.FullName -eq "extension/package.json" }
        $hasContentTypes = $zipArchive.Entries | Where-Object { $_.FullName -eq "[Content_Types].xml" }
        $zipArchive.Dispose()
        
        Write-Host "`nVSIX Structure Verification:" -ForegroundColor Yellow
        Write-Host "  - extension.vsixmanifest: $($null -ne $hasManifest)" -ForegroundColor White
        Write-Host "  - extension/package.json: $($null -ne $hasPackageJson)" -ForegroundColor White
        Write-Host "  - [Content_Types].xml: $($null -ne $hasContentTypes)" -ForegroundColor White
        
        if ($hasManifest -and $hasPackageJson -and $hasContentTypes) {
            Write-Host "✅ VSIX structure is valid!" -ForegroundColor Green
        } else {
            Write-Host "❌ VSIX structure may be invalid!" -ForegroundColor Red
        }
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

# Installation instructions
Write-Host "`nTo install the extension:" -ForegroundColor Cyan
Write-Host "  code --install-extension `"$vsixPath`"" -ForegroundColor White
Write-Host "`nOr via VS Code UI:" -ForegroundColor Cyan
Write-Host "  Extensions → ... → Install from VSIX → Select file" -ForegroundColor White
