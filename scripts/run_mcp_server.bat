@echo off 
REM Activate virtual environment 
call venv\Scripts\activate.bat 
 
REM Set environment variables 
set PYTHONPATH=%PYTHONPATH%;C:\Users\xufeisong\Desktop\workspace\mcp_device_management 
 
echo [START] Starting MCP HTTP/WebSocket Server... 
echo [INFO] Server address: http://localhost:8000 
echo [INFO] MCP WebSocket endpoint: ws://localhost:8000/mcp 
echo [INFO] Press Ctrl+C to stop server 
 
REM Run MCP server 
python run_mcp_server.py 
