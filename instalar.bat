@echo off
REM Prepara el entorno del Buscador de Duplicados.
REM Reutiliza ..\.venv_face si existe; si no, crea .venv aqui e instala lo necesario.
cd /d "%~dp0"
if exist "..\.venv_face\Scripts\python.exe" (
  set "PY=..\.venv_face\Scripts\python.exe"
  echo Usando el entorno compartido ..\.venv_face
) else (
  if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno .venv ...
    py -m venv .venv
  )
  set "PY=.venv\Scripts\python.exe"
)
echo Instalando dependencias...
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
echo.
echo Listo. Abre la app con  Buscar-duplicados.bat
pause
