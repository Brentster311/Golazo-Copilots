<#
.SYNOPSIS
    Launch SFI Reporter after ensuring Azure CLI authentication.

.DESCRIPTION
    1. Runs 'az login' so the user has a valid Azure token (no subscription prompt).
    2. Launches the SFI Reporter tkinter desktop app.
#>

# --- Azure login (no subscription selection) ---
Write-Host "Signing in to Azure..." -ForegroundColor Cyan
az login --only-show-errors | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Azure login failed. Please try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Azure login successful." -ForegroundColor Green

# --- Launch SFI Reporter ---
Write-Host "Starting SFI Reporter..." -ForegroundColor Cyan
& "$PSScriptRoot\SFIReporter.exe"
