@echo off
REM Build Javi.QL as a standalone Windows .exe using PyInstaller

echo.
echo ========================================
echo Building Javi.QL Standalone Executable
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Build the executable
echo [BUILD] Compiling executable...
pyinstaller --onefile --name JaviQL --icon=None --add-data "index.html;." ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.websockets ^
  --hidden-import uvicorn.protocols.websockets.auto ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.on ^
  main.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Build Complete!
echo ========================================
echo.
echo Executable: dist\JaviQL.exe
echo.
echo Next steps:
echo  1. Copy dist\JaviQL.exe to your distribution folder
echo  2. Create a .env file next to it with your database config
echo  3. Distribute as a zip file to teammates
echo  4. Teammates just double-click JaviQL.exe to run
echo.
pause
