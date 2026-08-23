# PowerShell helper to push repository to GitHub
param(
    [string]$Token
)

$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  NLP Project - Push to GitHub" -ForegroundColor Cyan
Write-Host "  Repository: https://github.com/imtiaz571/NLP" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$gitCmd = "git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    if (Test-Path "C:\Program Files\Git\cmd\git.exe") {
        $gitCmd = "C:\Program Files\Git\cmd\git.exe"
    } elseif (Test-Path "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe") {
        $gitCmd = "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    }
}

if (-not $Token) {
    $Token = Read-Host "Enter your GitHub Personal Access Token (or press ENTER to use standard login)"
}

try {
    if ($Token -and $Token.Trim() -ne "") {
        Write-Host "Pushing to GitHub using access token..." -ForegroundColor Yellow
        & $gitCmd push "https://$($Token.Trim())@github.com/imtiaz571/NLP.git" main
    } else {
        Write-Host "Pushing to GitHub using Git credentials..." -ForegroundColor Yellow
        & $gitCmd push origin main
    }
    Write-Host "`n[SUCCESS] All code has been successfully pushed to https://github.com/imtiaz571/NLP" -ForegroundColor Green
} catch {
    Write-Host "`n[ERROR] Push failed. $_" -ForegroundColor Red
}
