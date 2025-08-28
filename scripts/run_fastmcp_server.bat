@echo off
REM FastMCP测试服务器启动脚本

echo [START] Starting FastMCP Test Server...

REM 激活虚拟环境
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM 设置环境变量
echo [INFO] Setting environment variables...
set PYTHONPATH=%PYTHONPATH%;%cd%\src
set FASTMCP_HOST=localhost
set FASTMCP_PORT=8001
set LOG_LEVEL=INFO

REM 创建必要的目录
echo [INFO] Creating necessary directories...
if not exist "logs" mkdir logs

echo.
echo [INFO] FastMCP Test Server Configuration:
echo [INFO] - Host: %FASTMCP_HOST%
echo [INFO] - Port: %FASTMCP_PORT%
echo [INFO] - Transport: HTTP Stream
echo [INFO] - Tools: test_tool
echo [INFO] - Prompts: test_prompt
echo [INFO] - Server URL: http://%FASTMCP_HOST%:%FASTMCP_PORT%
echo.
echo [INFO] Press Ctrl+C to stop server
echo.

REM 启动MCP服务器
echo [START] Starting MCP HTTP Stream Server...
python src\mcp_server\fastmcp_test_server.py

echo.
echo [STOP] FastMCP Test Server stopped.
pause
