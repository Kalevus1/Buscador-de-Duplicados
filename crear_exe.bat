@echo off
REM Genera BuscadorDuplicados.exe (portatil, sin consola, con icono).
cd /d "%~dp0"
set "PYDIR=..\.venv_face\Scripts"
if not exist "%PYDIR%\python.exe" set "PYDIR=.venv\Scripts"
if not exist "%PYDIR%\pyinstaller.exe" (
  echo Instalando PyInstaller...
  "%PYDIR%\python.exe" -m pip install pyinstaller
)
"%PYDIR%\pyinstaller.exe" --noconfirm --clean --windowed --onedir ^
  --name "BuscadorDuplicados" --icon "recursos\icono.ico" ^
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets ^
  --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml ^
  --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtMultimedia ^
  --exclude-module PySide6.QtPdf --exclude-module PySide6.QtWebChannel ^
  --exclude-module PySide6.QtDesigner ^
  --exclude-module scipy --exclude-module jax --exclude-module jaxlib ^
  --exclude-module matplotlib --exclude-module pywt --exclude-module mediapipe ^
  --exclude-module cv2 --exclude-module tensorflow --exclude-module torch ^
  buscador_duplicados.py
echo.
echo Listo: dist\BuscadorDuplicados\BuscadorDuplicados.exe
pause
