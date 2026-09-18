@echo off
REM Abre el Buscador de Duplicados (Dia 11). Reutiliza el entorno ..\.venv_face o .venv.
cd /d "%~dp0"
set "PY=..\.venv_face\Scripts\pythonw.exe"
if not exist "%PY%" set "PY=.venv\Scripts\pythonw.exe"
if not exist "%PY%" (
  echo No encuentro el entorno. Ejecuta primero instalar.bat
  pause & exit /b 1
)
start "" "%PY%" buscador_duplicados.py
