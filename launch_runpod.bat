@echo off
setlocal

REM Check if the virtual environment exists
if not exist "%~dp0\venv\Scripts\activate" (
    echo Virtual environment not found. Running setup.bat to create it.
    call "%~dp0\setup.bat"
)

REM Activate the virtual environment
call "%~dp0\venv\Scripts\activate"

REM Run the Python script and capture any error
python "%~dp0\runpod_tab.py" 2> error.log

REM Check if there was an error
if %errorlevel% neq 0 (
    echo There was an error. See error.log for details.
    exit /b %errorlevel%
)

endlocal