# Clean Release Packager for Notice2Action AI (PS02)
# Windows PowerShell compatible
# Strictly excludes virtual environments, weights, caches, git, and secrets.

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ReleaseDir = Join-Path $ProjectRoot "release"
if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir | Out-Null
}

$ZipFile = Join-Path $ReleaseDir "notice2action_ps02_release.zip"
if (Test-Path $ZipFile) {
    Remove-Item -Force $ZipFile
}

$StagingDir = Join-Path $ReleaseDir "staging_notice2action"
if (Test-Path $StagingDir) {
    Remove-Item -Recurse -Force $StagingDir
}
New-Item -ItemType Directory -Path $StagingDir | Out-Null

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Staging clean release files..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Define allowed files and folders
$ItemsToCopy = @(
    "src",
    "tests",
    "scripts",
    "docs",
    "assets",
    "reports",
    ".streamlit",
    "app.py",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "UI_INTERACTION_TEST_MATRIX.md",
    "FINAL_FUNCTIONALITY_AUDIT.md",
    "FINAL_TEST_RESULTS.md",
    "FINAL_BUG_FIX_LOG.md",
    ".env.example",
    ".gitignore"
)

foreach ($item in $ItemsToCopy) {
    $srcPath = Join-Path $ProjectRoot $item
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $StagingDir -Recurse -Force
        Write-Host "  Included: $item" -ForegroundColor Green
    }
}

# Clean any pycache or pytest_cache from staging
Get-ChildItem -Path $StagingDir -Include "__pycache__", ".pytest_cache" -Recurse -Force | Remove-Item -Recurse -Force

# Create ZIP archive
Write-Host "`nCompressing clean archive to $ZipFile..." -ForegroundColor Yellow
Compress-Archive -Path "$StagingDir\*" -DestinationPath $ZipFile -CompressionLevel Optimal

# Clean up staging directory
Remove-Item -Recurse -Force $StagingDir

# Verify ZIP contents
Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " Release Archive Created: $ZipFile" -ForegroundColor Green
$zipSize = (Get-Item $ZipFile).Length / 1MB
Write-Host " Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Green

# Inspect zip contents
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($ZipFile)
Write-Host "`nArchive File Count: $($archive.Entries.Count)" -ForegroundColor Cyan
$sampleEntries = $archive.Entries | Select-Object -First 15
Write-Host "Sample Entries:" -ForegroundColor Gray
foreach ($e in $sampleEntries) {
    Write-Host "  - $($e.FullName)" -ForegroundColor Gray
}
$archive.Dispose()
Write-Host "==========================================================" -ForegroundColor Green
