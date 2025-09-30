@echo off
echo ========================================
echo TextPin - 文字剪贴板工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10或更高版本
    pause
    exit /b 1
)

echo [信息] 检查依赖...
pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo [信息] 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [信息] 启动应用程序...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo [错误] 应用程序运行出错
    pause
)
