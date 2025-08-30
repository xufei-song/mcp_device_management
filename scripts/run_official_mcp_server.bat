@echo off
REM 启动官方MCP SDK实现的测试设备管理服务器

echo [INFO] 启动官方MCP SDK测试设备管理服务器...
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] 虚拟环境未找到！
    echo [INFO] 请先运行 scripts\setup.bat 创建虚拟环境并安装依赖
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [INFO] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 验证激活状态
if "%VIRTUAL_ENV%"=="" (
    echo [ERROR] 虚拟环境激活失败！
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] 虚拟环境已激活: %VIRTUAL_ENV%

REM 检查MCP依赖
echo [INFO] 检查MCP依赖...
python -c "import mcp; print('[SUCCESS] MCP SDK 已安装')" 2>nul
if errorlevel 1 (
    echo [ERROR] MCP SDK 未安装！
    echo [INFO] 正在安装MCP SDK...
    pip install mcp
    if errorlevel 1 (
        echo [ERROR] MCP SDK 安装失败！
        pause
        exit /b 1
    )
)

REM 设置Python路径
set PYTHONPATH=%PYTHONPATH%;%cd%

REM 创建日志目录
if not exist "logs" mkdir logs

REM 运行Python启动脚本
echo.
echo [INFO] 启动MCP服务器...
echo [INFO] 按 Ctrl+C 停止服务器
echo.
python scripts\run_official_mcp_server.py

echo.
echo [INFO] 服务器已停止
pause
