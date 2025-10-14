@echo off
echo ============================================================
echo.
echo   TextPin Clean Tool
echo   Remove all build artifacts
echo.
echo ============================================================
echo.

cd ..

echo [1/5] Cleaning build directory...
if exist "build" (
    rmdir /s /q build
    echo [OK] Removed build/
) else (
    echo [-] build/ does not exist
)

echo.
echo [2/5] Cleaning dist directory...
if exist "dist" (
    rmdir /s /q dist
    echo [OK] Removed dist/
) else (
    echo [-] dist/ does not exist
)

echo.
echo [3/5] Cleaning installer directory...
if exist "installer" (
    rmdir /s /q installer
    echo [OK] Removed installer/
) else (
    echo [-] installer/ does not exist
)

echo.
echo [4/5] Cleaning generated config files...
if exist "TextPin.spec" (
    del /q TextPin.spec
    echo [OK] Removed TextPin.spec
)
if exist "TextPin_Setup.iss" (
    del /q TextPin_Setup.iss
    echo [OK] Removed TextPin_Setup.iss
)
if exist "LICENSE.txt" (
    del /q LICENSE.txt
    echo [OK] Removed LICENSE.txt
)
if exist "README_INSTALL.txt" (
    del /q README_INSTALL.txt
    echo [OK] Removed README_INSTALL.txt
)

echo.
echo [5/5] Cleaning Python cache...
for /d /r %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d"
    echo [OK] Removed %%d
)

echo.
echo ============================================================
echo.
echo Clean complete!
echo.
echo Project is now clean and ready for rebuild.
echo.
pause
