@echo off
REM MCP Test Device Management System Environment Activation Script (Windows)

echo [INFO] Activating MCP Test Device Management System environment...

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo [TIP] Please run setup.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    echo.
    echo [TIP] Please check if the virtual environment is corrupted.
    echo [TIP] Try running setup.bat again to recreate it.
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated successfully!

REM Set Python path to include src directory
echo [INFO] Setting Python path...
set PYTHONPATH=%PYTHONPATH%;%cd%\src

REM Set default environment variables (can be overridden by .env file)
echo [INFO] Setting default environment variables...
set MCP_SERVER_HOST=localhost
set MCP_SERVER_PORT=8000
set LOG_LEVEL=INFO
set DEBUG_MODE=true

REM Load environment variables from .env file if it exists
if exist ".env" (
    echo [INFO] Loading environment variables from .env file...
    for /f "tokens=1,* delims==" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
    echo [SUCCESS] Environment variables loaded from .env
) else (
    echo [WARNING] .env file not found, using default values
    echo [TIP] You can create .env from env.template for custom configuration
)


REM Verify Python and key packages
echo [INFO] Verifying Python environment...
python --version
if errorlevel 1 (
    echo [ERROR] Python not accessible in virtual environment!
    pause
    exit /b 1
)

echo [INFO] Checking key packages...
python -c "import fastapi, uvicorn, pydantic" 2>nul
if errorlevel 1 (
    echo [WARNING] Some required packages may not be installed
    echo [TIP] Run: pip install -e .[dev]
)

echo.
echo [SUCCESS] Environment activation completed!
echo.
echo [INFO] Current working directory: %cd%
echo [INFO] Python executable: %where python%
echo [INFO] Virtual environment: %VIRTUAL_ENV%
echo [INFO] Server will run on: %MCP_SERVER_HOST%:%MCP_SERVER_PORT%
echo [INFO] Log level: %LOG_LEVEL%
echo.
echo [TIP] To deactivate, type: deactivate
echo [TIP] To reactivate later, run: scripts\activate.bat
echo.

REM Keep the command prompt open with activated environment
echo [INFO] Environment is now active. You can run Python commands or start the server.
echo.
cmd /k
