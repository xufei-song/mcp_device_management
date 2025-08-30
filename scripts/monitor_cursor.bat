@echo off 
REM Activate virtual environment 
call venv\Scripts\activate.bat 
 
REM Set environment variables 
set PYTHONPATH=%PYTHONPATH%;D:\work\workspace\TestDeviceManagmentMCP 
echo [START] Starting Cursor MCP execution monitor... 
