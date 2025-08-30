@echo off
setlocal enabledelayedexpansion

echo ========================================
echo 启动MCP服务器2 (官方SDK StreamableHTTP)
echo ========================================

:: 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 虚拟环境不存在
    echo 请先运行: scripts\setup.bat
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 激活虚拟环境...
call "venv\Scripts\activate.bat"

:: 检查虚拟环境是否激活成功
if "%VIRTUAL_ENV%"=="" (
    echo 错误: 虚拟环境激活失败
    pause
    exit /b 1
)

echo 虚拟环境已激活: %VIRTUAL_ENV%

:: 检查MCP SDK
echo 检查MCP SDK...
python -c "import mcp, mcp.server, mcp.types; print('MCP SDK已安装并可用')" 2>nul
if !errorlevel! neq 0 (
    echo 错误: MCP SDK未安装
    echo 正在安装MCP SDK...
    pip install mcp
    if !errorlevel! neq 0 (
        echo MCP SDK安装失败
        pause
        exit /b 1
    )
)

:: 启动服务器
echo.
echo 启动MCP服务器2...
echo 端口: 8002
echo 端点: http://127.0.0.1:8002/mcp
echo 传输: StreamableHTTP (官方SDK)
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================

python scripts\run_mcp_server2.py

pause
