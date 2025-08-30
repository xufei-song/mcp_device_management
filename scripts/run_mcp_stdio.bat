@echo off 
REM Activate virtual environment 
call venv\Scripts\activate.bat 
 
REM Set environment variables 
set PYTHONPATH=%PYTHONPATH%;D:\work\workspace\TestDeviceManagmentMCP 
 
echo [START] Starting MCP stdio server for Cursor integration... 
echo [INFO] This server communicates via stdin/stdout 
echo [INFO] Press Ctrl+C to stop server 
 
REM Run MCP stdio server 
python mcp_stdio_server.py 
 
echo [INFO] This script monitors MCP server execution 
echo [INFO] Press Ctrl+C to stop monitoring 
 
REM Run monitoring script 
python monitor_cursor_execution.py 
