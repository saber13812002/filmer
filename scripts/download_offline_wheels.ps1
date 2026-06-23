# دانلود wheelهای Linux/Python3.12 برای نصب آفلاین روی سرور
# اجرا در PowerShell از ریشه پروژه:
#   .\scripts\download_offline_wheels.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$WheelsDir   = Join-Path $ProjectRoot "offline-wheels"
$ReqFile     = Join-Path $ProjectRoot "requirements.txt"

# تگ‌های هدف: سرور Linux x86_64 + Python 3.12
$Platform    = "manylinux2014_x86_64"
$PyVersion   = "312"

Write-Host "=== Filmer: Download offline wheels ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
Write-Host "Output:  $WheelsDir"
Write-Host "Target:  Linux / Python 3.12 / $Platform"
Write-Host ""

if (-not (Test-Path $ReqFile)) {
    throw "requirements.txt not found: $ReqFile"
}

# pip موجود باشد
$pip = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pip) {
    $pip = Get-Command pip3 -ErrorAction SilentlyContinue
}
if (-not $pip) {
    throw "pip not found. Install Python 3 and ensure pip is on PATH."
}

New-Item -ItemType Directory -Force -Path $WheelsDir | Out-Null

# پاک کردن wheelهای قبلی (اختیاری — برای دانلود تمیز)
Get-ChildItem -Path $WheelsDir -Filter "*.whl" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path $WheelsDir -Filter "*.tar.gz" -ErrorAction SilentlyContinue | Remove-Item -Force

Write-Host "[1/2] Downloading wheels for Linux cp$PyVersion ..." -ForegroundColor Yellow

& $pip.Source download `
    -r $ReqFile `
    -d $WheelsDir `
    --platform $Platform `
    --python-version $PyVersion `
    --implementation cp `
    --abi "cp$PyVersion" `
    --only-binary=:all:

if ($LASTEXITCODE -ne 0) {
    Write-Host "Retrying with source allowed for missing binaries ..." -ForegroundColor DarkYellow
    & $pip.Source download `
        -r $ReqFile `
        -d $WheelsDir `
        --platform $Platform `
        --python-version $PyVersion `
        --implementation cp `
        --abi "cp$PyVersion"
}

Write-Host "[2/2] Writing manifest ..." -ForegroundColor Yellow

$manifest = @(
    "generated_at=$(Get-Date -Format o)"
    "pip_version=$((& $pip.Source --version 2>&1) -join ' ')"
    "python_version=$((python --version 2>&1) -join ' ')"
    "target_platform=$Platform"
    "target_python=3.12"
    "wheel_count=$((Get-ChildItem $WheelsDir -Include *.whl,*.tar.gz -Recurse).Count)"
)
$manifest | Set-Content -Encoding UTF8 (Join-Path $WheelsDir "MANIFEST.txt")

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
Write-Host "Wheels saved to: offline-wheels\"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  git add offline-wheels/"
Write-Host "  git commit -m ""Add offline Python wheels for server install"""
Write-Host "  git push"
Write-Host "  Then tell the agent to run: bash scripts/install_offline_wheels.sh"
