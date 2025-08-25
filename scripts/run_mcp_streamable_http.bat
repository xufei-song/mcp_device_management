@echo off
echo 启动 MCP Streamable HTTP 服务器...
echo.

REM 激活虚拟环境
call scripts\activate.bat

REM 设置环境变量
set PYTHONPATH=%cd%\src
set PYTHONIOENCODING=utf-8

REM 安装依赖（如果需要）
echo 检查依赖...
pip install fastapi uvicorn sse-starlette aiohttp

REM 启动服务器
echo 启动服务器在 http://127.0.0.1:8000
echo 按 Ctrl+C 停止服务器
echo.

python src\mcp\streamable_http_server.py

pause
