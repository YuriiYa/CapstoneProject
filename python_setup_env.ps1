# Setup script for creating a clean Python environment

if (Test-Path "venv") {
    Write-Host "Virtual environment already exists. Activating..."
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating virtual environment..."
    python -m venv venv

    Write-Host "Activating virtual environment..."
    .\venv\Scripts\Activate.ps1

    Write-Host "Upgrading pip..."
    python -m pip install --upgrade pip

    Write-Host "Installing requirements..."
    pip install -r requirements.txt

    Write-Host ""
    Write-Host "Setup complete!"
}

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host ""
Write-Host "To activate the environment in the future, run:"
Write-Host "  .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To run the Flask API:"
Write-Host "  python api\app.py"
Write-Host ""
