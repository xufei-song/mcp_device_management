@echo off
REM FastMCP测试客户端脚本

echo [START] Starting FastMCP Test Client...

REM 激活虚拟环境
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM 设置环境变量
echo [INFO] Setting environment variables...
set PYTHONPATH=%PYTHONPATH%;%cd%\src

echo.
echo [INFO] FastMCP Test Client Configuration:
echo [INFO] - Target Server: http://localhost:8001
echo [INFO] - Testing tools: test_tool
echo [INFO] - Testing prompts: test_prompt
echo.
echo [INFO] Make sure FastMCP server is running (run_fastmcp_server.bat)
echo.

REM 运行测试客户端
echo [START] Running MCP Test Client...
python src\mcp_server\test_fastmcp_client.py

echo.
echo [COMPLETE] FastMCP Test Client finished.
pause
