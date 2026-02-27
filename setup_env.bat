@echo off
REM Setup script for creating a clean Python environment

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To activate the environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the Flask API:
echo   python api\app.py
echo.
pause
