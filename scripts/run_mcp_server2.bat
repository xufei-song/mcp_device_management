@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Starting MCP Server 2 (Official SDK StreamableHTTP)
echo ========================================

:: Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please run: scripts\setup.bat
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call "venv\Scripts\activate.bat"

:: Check if virtual environment activation succeeded
if "%VIRTUAL_ENV%"=="" (
    echo Error: Virtual environment activation failed
    pause
    exit /b 1
)

echo Virtual environment activated: %VIRTUAL_ENV%

:: Check MCP SDK
echo Checking MCP SDK...
python -c "import mcp, mcp.server, mcp.types; print('MCP SDK installed and available')" 2>nul
if !errorlevel! neq 0 (
    echo Error: MCP SDK not installed
    echo Installing MCP SDK...
    pip install mcp
    if !errorlevel! neq 0 (
        echo MCP SDK installation failed
        pause
        exit /b 1
    )
)

:: Start server
echo.
echo Starting MCP Server 2...
echo Port: 8002
echo Endpoint: http://127.0.0.1:8002/mcp
echo Transport: StreamableHTTP (Official SDK)
echo.
echo Press Ctrl+C to stop server
echo ========================================

python scripts\run_mcp_server2.py

pause
