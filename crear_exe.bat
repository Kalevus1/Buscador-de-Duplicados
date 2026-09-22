@echo off
REM Genera el ejecutable en DOS formatos:
REM   1) CARPETA  -> dist\BuscadorDuplicados\        (arranca rapido)
REM   2) EMPAQUETADO -> dist\BuscadorDuplicados.exe  (un solo archivo portatil)
cd /d "%~dp0"
set "PYDIR=..\.venv_face\Scripts"
if not exist "%PYDIR%\python.exe" set "PYDIR=.venv\Scripts"
if not exist "%PYDIR%\pyinstaller.exe" (
  echo Instalando PyInstaller...
  "%PYDIR%\python.exe" -m pip install pyinstaller
)

set EXCL=--exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtPdf --exclude-module PySide6.QtWebChannel --exclude-module PySide6.QtDesigner --exclude-module scipy --exclude-module jax --exclude-module jaxlib --exclude-module matplotlib --exclude-module pywt --exclude-module mediapipe --exclude-module cv2 --exclude-module tensorflow --exclude-module torch

echo === 1/2  Version CARPETA (onedir) ===
"%PYDIR%\pyinstaller.exe" --noconfirm --clean --windowed --onedir ^
  --name "BuscadorDuplicados" --icon "recursos\icono.ico" %EXCL% buscador_duplicados.py

echo === 2/2  Version EMPAQUETADA (onefile) ===
"%PYDIR%\pyinstaller.exe" --noconfirm --windowed --onefile ^
  --name "BuscadorDuplicados" --icon "recursos\icono.ico" %EXCL% buscador_duplicados.py

echo.
echo Listo:
echo   Carpeta      -^> dist\BuscadorDuplicados\BuscadorDuplicados.exe
echo   Empaquetado  -^> dist\BuscadorDuplicados.exe  (un solo archivo)
pause
