@echo off 
REM Activate virtual environment 
call venv\Scripts\activate.bat 
 
REM Set environment variables 
set PYTHONPATH=%PYTHONPATH%;D:\work\workspace\TestDeviceManagmentMCP\src 
set MCP_SERVER_HOST=localhost 
set MCP_SERVER_PORT=8000 
set LOG_LEVEL=DEBUG 
 
REM Create necessary directories 
if not exist "logs" mkdir logs 
if not exist "data" mkdir data 
 
echo [START] Starting MCP Test Device Management System development server... 
echo [INFO] Server address: http://localhost:8000 
echo [INFO] API documentation: http://localhost:8000/docs 
echo [INFO] Press Ctrl+C to stop server 
 
REM Run development server 
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 
