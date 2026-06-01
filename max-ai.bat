@echo off
cd /d "%~dp0"
rem If arguments provided, run CLI; otherwise run tray in background
if "%~1"=="" (
	start "" pythonw -m max_ai.tray
) else (
	python -m max_ai.cli %*
)