<#
PowerShell helper to create a Python venv and install backend dependencies.
Run from repository root in PowerShell as: .\scripts\setup_env.ps1

This script does not install Node or npm. It can optionally run `npm install` if you have Node installed.
#>

param(
    [switch]$InstallFrontend
)

Write-Host "Setting up Python virtual environment in .venv..."

if (-not (Test-Path -Path .venv)) {
    python -m venv .venv
} else {
    Write-Host ".venv already exists, skipping creation."
}

Write-Host "Activating venv..."
. .venv\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing backend requirements..."
python -m pip install --upgrade pip setuptools wheel
pip install -r backend\requirements.txt

if ($InstallFrontend) {
    if (Test-Path 'frontend-vite\package.json') {
        Write-Host "Installing frontend dependencies (requires Node.js/npm)..."
        Push-Location frontend-vite
        npm install
        Pop-Location
    } else {
        Write-Host "No frontend package.json found at frontend-vite/package.json"
    }
}

Write-Host "Setup complete. Activate venv with: .\.venv\Scripts\Activate.ps1"
