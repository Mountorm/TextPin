@echo off
echo ============================================================
echo.
echo   TextPin Build Tool
echo.
echo ============================================================
echo.

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Check dependencies
echo [1/4] Checking dependencies...
pip show pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Installing PyInstaller...
    pip install pyinstaller
)

pip show pillow >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Installing Pillow...
    pip install pillow
)
echo [OK] Dependencies ready
echo.

REM Create icon
echo [2/4] Creating icon...
cd ..
if not exist "resources\icon.ico" (
    cd build_tools
    python create_icon.py
    cd ..
) else (
    echo [OK] Icon already exists
)
echo.

REM Build
echo [3/4] Building...
cd build_tools
python build_installer.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed!
    cd ..
    pause
    exit /b 1
)
cd ..
echo.

REM Done
echo [4/4] Build complete!
echo.
echo ============================================================
echo.
echo Output:
echo   Executable: build_tools\dist\TextPin\TextPin.exe
echo   Installer:  build_tools\installer\TextPin_Setup_v2.0.3.exe
echo.
echo Press any key to open output folders...
pause >nul

REM Open output folders
if exist "build_tools\dist\TextPin" (
    explorer build_tools\dist\TextPin
)

if exist "build_tools\installer" (
    explorer build_tools\installer
)
