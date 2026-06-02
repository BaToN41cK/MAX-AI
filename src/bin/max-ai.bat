@echo off
setlocal
set SCRIPT_DIR=%~dp0
set PYTHONPATH=%SCRIPT_DIR%..
rem If arguments provided, run CLI; otherwise run tray in background
if "%~1"=="" (
	start "" pythonw -m max_ai.tray
) else (
	python -m max_ai.cli %*
)
endlocal