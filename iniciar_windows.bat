@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo Falha na instalacao / Installation failed.
  echo Instale Python de python.org / Install Python from python.org
  echo Marque / Enable: Add Python to PATH.
  pause
  exit /b 1
)
py app.py
if errorlevel 1 pause
