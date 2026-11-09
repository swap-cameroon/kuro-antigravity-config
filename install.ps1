# Installation script for Team Kuro Antigravity Configuration
# Run this on your target machine: .\install.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Installing Team Kuro for Antigravity" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$targetDir = "$HOME\.gemini\config"

if (-not (Test-Path $targetDir)) {
    Write-Host "Creating $targetDir..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
}

$scriptDir = $PSScriptRoot

Write-Host "Deploying Team Kuro plugins and rules..." -ForegroundColor Green
Copy-Item -Recurse -Force "$scriptDir\plugins" "$targetDir\"

Write-Host "Deploying 32 specialized skills..." -ForegroundColor Green
Copy-Item -Recurse -Force "$scriptDir\skills" "$targetDir\"

Write-Host "Deploying base configurations..." -ForegroundColor Green
Copy-Item -Force "$scriptDir\config.json" "$targetDir\"
Copy-Item -Force "$scriptDir\hooks.json" "$targetDir\"
Copy-Item -Force "$scriptDir\mcp_config.json" "$targetDir\"

Write-Host "`nValidating installation with Antigravity CLI..." -ForegroundColor Cyan
try {
    agy plugins list
    Write-Host "`n✔ Team Kuro is fully operational on this machine!" -ForegroundColor Green
} catch {
    Write-Host "`nConfiguration deployed successfully! (Run 'agy plugins list' after installing agy)" -ForegroundColor Yellow
}
