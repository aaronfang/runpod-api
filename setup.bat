@echo off
set script_dir=%~dp0

echo "Setting up virtual environment..."
if not exist "%script_dir%\venv" (
    python -m venv "%script_dir%\venv"
)
echo "Activating virtual environment..."
call "%script_dir%\venv\Scripts\activate"
echo "Installing requirements..."
pip install -r "%script_dir%\requirements.txt"

echo "Setup complete"

exit /b 0
