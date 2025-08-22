@echo off 
REM Activate virtual environment 
call venv\Scripts\activate.bat 
 
REM Set environment variables 
set PYTHONPATH=%PYTHONPATH%;D:\work\workspace\TestDeviceManagmentMCP\src 
 
echo 🧪 Running tests... 
pytest tests\ -v --cov=src --cov-report=html --cov-report=term-missing 
