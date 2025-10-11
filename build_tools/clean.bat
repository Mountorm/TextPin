@echo off
chcp 65001 >nul
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   TextPin 清理工具                                        ║
echo ║   清理打包生成的临时文件                                  ║
echo ║                                                           ║
╚═══════════════════════════════════════════════════════════╝
echo.

cd ..

echo [1/5] 清理 build 目录...
if exist "build" (
    rmdir /s /q build
    echo ✓ 已删除 build/
) else (
    echo - build/ 不存在
)

echo.
echo [2/5] 清理 dist 目录...
if exist "dist" (
    rmdir /s /q dist
    echo ✓ 已删除 dist/
) else (
    echo - dist/ 不存在
)

echo.
echo [3/5] 清理 installer 目录...
if exist "installer" (
    rmdir /s /q installer
    echo ✓ 已删除 installer/
) else (
    echo - installer/ 不存在
)

echo.
echo [4/5] 清理自动生成的配置文件...
if exist "TextPin.spec" (
    del /q TextPin.spec
    echo ✓ 已删除 TextPin.spec
)
if exist "TextPin_Setup.iss" (
    del /q TextPin_Setup.iss
    echo ✓ 已删除 TextPin_Setup.iss
)
if exist "LICENSE.txt" (
    del /q LICENSE.txt
    echo ✓ 已删除 LICENSE.txt
)
if exist "README_INSTALL.txt" (
    del /q README_INSTALL.txt
    echo ✓ 已删除 README_INSTALL.txt
)

echo.
echo [5/5] 清理 Python 缓存...
for /d /r %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d"
    echo ✓ 已删除 %%d
)

echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ✓ 清理完成！
echo.
echo 项目已恢复到干净状态，可以重新打包。
echo.
pause
