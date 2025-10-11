@echo off
chcp 65001 >nul
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║   TextPin 一键打包工具                                    ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python！
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [✓] 找到 Python
python --version
echo.

REM 检查依赖
echo [1/4] 检查依赖...
pip show pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] PyInstaller 未安装，正在安装...
    pip install pyinstaller
)

pip show pillow >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Pillow 未安装，正在安装...
    pip install pillow
)
echo [✓] 依赖检查完成
echo.

REM 创建图标
echo [2/4] 创建图标...
if not exist "resources\icon.ico" (
    python create_icon.py
) else (
    echo [✓] 图标已存在
)
echo.

REM 执行打包
echo [3/4] 开始打包...
python build_installer.py
if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)
echo.

REM 完成
echo [4/4] 打包完成！
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo 打包结果：
echo   可执行文件: dist\TextPin\TextPin.exe
echo   安装程序: installer\TextPin_Setup_v2.0.0.exe
echo.
echo 按任意键打开输出目录...
pause >nul

REM 打开输出目录
if exist "dist\TextPin" (
    explorer dist\TextPin
)

if exist "installer" (
    explorer installer
)
