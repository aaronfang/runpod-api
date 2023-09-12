@echo off
set script_dir=%~dp0

%script_dir%\venv\Scripts\python "%script_dir%get_pods.py" %*