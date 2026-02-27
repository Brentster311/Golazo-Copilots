param(
    [switch]$SkipTests,
    [switch]$NoClean
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$guiDir = Join-Path $repoRoot "GUI"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Push-Location $guiDir
try {
    if (-not $SkipTests) {
        & $pythonExe -m pytest tests/ -v
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed. Build aborted."
        }
    }

    $buildArgs = @("-m", "PyInstaller")
    if (-not $NoClean) {
        $buildArgs += "--clean"
    }
    $buildArgs += "S360Reporter.spec"

    & $pythonExe @buildArgs
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    Compress-Archive -Path "dist/S360Reporter.exe", "README.md" -DestinationPath "dist/S360Reporter.zip" -Force

    Write-Host "Build complete: GUI/dist/S360Reporter.exe"
    Write-Host "Package complete: GUI/dist/S360Reporter.zip"
}
finally {
    Pop-Location
}
