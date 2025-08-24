@echo off
REM MCP Test Device Management System Setup Script (Windows)

echo [START] Starting MCP Test Device Management System setup...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found, please install Python 3.8 or higher first
    pause
    exit /b 1
)

echo [SUCCESS] Python version check passed

REM Create virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
) else (
    echo [SUCCESS] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install project dependencies
echo [INFO] Installing project dependencies...
pip install -e .

REM Install development dependencies
echo [INFO] Installing development dependencies...
pip install -e ".[dev]"

REM Install additional required packages
echo [INFO] Installing additional required packages...
pip install python-dotenv
pip install psutil
pip install websockets
pip install pytest
pip install pytest-cov
pip install pytest-asyncio
pip install httpx
pip install aiofiles
pip install pyyaml
pip install jinja2
pip install python-multipart

REM Create necessary directories
echo [INFO] Creating project directories...
if not exist "src" mkdir src
if not exist "src\mcp" mkdir src\mcp
if not exist "src\device" mkdir src\device
if not exist "src\handlers" mkdir src\handlers
if not exist "src\utils" mkdir src\utils
if not exist "config" mkdir config
if not exist "tests" mkdir tests
if not exist "docs" mkdir docs
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
if not exist "downloads" mkdir downloads
if not exist ".vscode" mkdir .vscode

REM Create __init__.py files
echo [INFO] Creating Python package files...
if not exist "src\__init__.py" type nul > src\__init__.py
if not exist "src\mcp\__init__.py" type nul > src\mcp\__init__.py
if not exist "src\device\__init__.py" type nul > src\device\__init__.py
if not exist "src\handlers\__init__.py" type nul > src\handlers\__init__.py
if not exist "src\utils\__init__.py" type nul > src\utils\__init__.py
if not exist "tests\__init__.py" type nul > tests\__init__.py

REM Create sample device directories
echo [INFO] Creating device directories...
if not exist "Devices\Android" mkdir Devices\Android
if not exist "Devices\IOS" mkdir Devices\IOS
if not exist "Devices\Windows" mkdir Devices\Windows

REM Create sample device files
echo [INFO] Creating sample device files...
echo # Android Device Directory > Devices\Android\README.md
echo. >> Devices\Android\README.md
echo Place Android device related files and configurations in this directory. >> Devices\Android\README.md

echo # iOS Device Directory > Devices\IOS\README.md
echo. >> Devices\IOS\README.md
echo Place iOS device related files and configurations in this directory. >> Devices\IOS\README.md

echo # Windows Device Directory > Devices\Windows\README.md
echo. >> Devices\Windows\README.md
echo Place Windows device related files and configurations in this directory. >> Devices\Windows\README.md

REM Create environment variable file
echo [INFO] Creating environment variable file...
if exist "env.template" (
    copy "env.template" ".env" >nul
    echo [SUCCESS] Environment file created from template
) else (
    echo [WARNING] env.template not found, creating basic .env file
    echo # MCP Server Configuration > .env
    echo MCP_SERVER_HOST=localhost >> .env
    echo MCP_SERVER_PORT=8000 >> .env
    echo LOG_LEVEL=INFO >> .env
    echo. >> .env
    echo # Device Discovery Configuration >> .env
    echo DEVICE_DISCOVERY_INTERVAL=30 >> .env
    echo ANDROID_AUTO_DISCOVER=true >> .env
    echo IOS_AUTO_DISCOVER=true >> .env
    echo WINDOWS_AUTO_DISCOVER=false >> .env
)

REM Create startup scripts
echo [INFO] Creating startup scripts...
echo @echo off > scripts\run_dev.bat
echo REM Activate virtual environment >> scripts\run_dev.bat
echo call venv\Scripts\activate.bat >> scripts\run_dev.bat
echo. >> scripts\run_dev.bat
echo REM Set environment variables >> scripts\run_dev.bat
echo set PYTHONPATH=%%PYTHONPATH%%;%cd%\src >> scripts\run_dev.bat
echo set MCP_SERVER_HOST=localhost >> scripts\run_dev.bat
echo set MCP_SERVER_PORT=8000 >> scripts\run_dev.bat
echo set LOG_LEVEL=DEBUG >> scripts\run_dev.bat
echo. >> scripts\run_dev.bat
echo REM Create necessary directories >> scripts\run_dev.bat
echo if not exist "logs" mkdir logs >> scripts\run_dev.bat
echo if not exist "data" mkdir data >> scripts\run_dev.bat
echo. >> scripts\run_dev.bat
echo echo [START] Starting MCP Test Device Management System development server... >> scripts\run_dev.bat
echo echo [INFO] Server address: http://localhost:8000 >> scripts\run_dev.bat
echo echo [INFO] API documentation: http://localhost:8000/docs >> scripts\run_dev.bat
echo echo [INFO] Press Ctrl+C to stop server >> scripts\run_dev.bat
echo. >> scripts\run_dev.bat
echo REM Run development server >> scripts\run_dev.bat
echo python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 >> scripts\run_dev.bat

REM Create test script
echo [INFO] Creating test script...
echo @echo off > scripts\run_tests.bat
echo REM Activate virtual environment >> scripts\run_tests.bat
echo call venv\Scripts\activate.bat >> scripts\run_tests.bat
echo. >> scripts\run_tests.bat
echo REM Set environment variables >> scripts\run_tests.bat
echo set PYTHONPATH=%%PYTHONPATH%%;%cd%\src >> scripts\run_tests.bat
echo. >> scripts\run_tests.bat
echo echo [INFO] Running tests... >> scripts\run_tests.bat
echo pytest tests\ -v --cov=src --cov-report=html --cov-report=term-missing >> scripts\run_tests.bat

REM Create MCP server script
echo [INFO] Creating MCP server script...
echo @echo off > scripts\run_mcp_server.bat
echo REM Activate virtual environment >> scripts\run_mcp_server.bat
echo call venv\Scripts\activate.bat >> scripts\run_mcp_server.bat
echo. >> scripts\run_mcp_server.bat
echo REM Set environment variables >> scripts\run_mcp_server.bat
echo set PYTHONPATH=%%PYTHONPATH%%;%cd% >> scripts\run_mcp_server.bat
echo. >> scripts\run_mcp_server.bat
echo echo [START] Starting MCP HTTP/WebSocket Server... >> scripts\run_mcp_server.bat
echo echo [INFO] Server address: http://localhost:8000 >> scripts\run_mcp_server.bat
echo echo [INFO] MCP WebSocket endpoint: ws://localhost:8000/mcp >> scripts\run_mcp_server.bat
echo echo [INFO] Press Ctrl+C to stop server >> scripts\run_mcp_server.bat
echo. >> scripts\run_mcp_server.bat
echo REM Run MCP server >> scripts\run_mcp_server.bat
echo python run_mcp_server.py >> scripts\run_mcp_server.bat

REM Create MCP stdio server script
echo [INFO] Creating MCP stdio server script...
echo @echo off > scripts\run_mcp_stdio.bat
echo REM Activate virtual environment >> scripts\run_mcp_stdio.bat
echo call venv\Scripts\activate.bat >> scripts\run_mcp_stdio.bat
echo. >> scripts\run_mcp_stdio.bat
echo REM Set environment variables >> scripts\run_mcp_stdio.bat
echo set PYTHONPATH=%%PYTHONPATH%%;%cd% >> scripts\run_mcp_stdio.bat
echo. >> scripts\run_mcp_stdio.bat
echo echo [START] Starting MCP stdio server for Cursor integration... >> scripts\run_mcp_stdio.bat
echo echo [INFO] This server communicates via stdin/stdout >> scripts\run_mcp_stdio.bat
echo echo [INFO] Press Ctrl+C to stop server >> scripts\run_mcp_stdio.bat
echo. >> scripts\run_mcp_stdio.bat
echo REM Run MCP stdio server >> scripts\run_mcp_stdio.bat
echo python mcp_stdio_server.py >> scripts\run_mcp_stdio.bat

REM Create monitoring script
echo [INFO] Creating monitoring script...
echo @echo off > scripts\monitor_cursor.bat
echo REM Activate virtual environment >> scripts\monitor_cursor.bat
echo call venv\Scripts\activate.bat >> scripts\monitor_cursor.bat
echo. >> scripts\monitor_cursor.bat
echo REM Set environment variables >> scripts\monitor_cursor.bat
echo set PYTHONPATH=%%PYTHONPATH%%;%cd% >> scripts\monitor_cursor.bat
echo. >> scripts\run_mcp_stdio.bat
echo echo [START] Starting Cursor MCP execution monitor... >> scripts\monitor_cursor.bat
echo echo [INFO] This script monitors MCP server execution >> scripts\run_mcp_stdio.bat
echo echo [INFO] Press Ctrl+C to stop monitoring >> scripts\run_mcp_stdio.bat
echo. >> scripts\run_mcp_stdio.bat
echo REM Run monitoring script >> scripts\run_mcp_stdio.bat
echo python monitor_cursor_execution.py >> scripts\run_mcp_stdio.bat

echo.
echo [SUCCESS] Setup completed!
echo.
echo [NEXT] Next steps:
echo 1. Environment file created: .env (from env.template)
echo 2. Configuration file ready: config\settings.yaml
echo 3. Start development server: scripts\run_dev.bat
echo 4. Start MCP HTTP server: scripts\run_mcp_server.bat
echo 5. Start MCP stdio server: scripts\run_mcp_stdio.bat
echo 6. Monitor Cursor integration: scripts\monitor_cursor.bat
echo 7. Run tests: scripts\run_tests.bat
echo.
echo [DOCS] View development documentation: DEVELOPMENT_GUIDE.md
echo [API] API documentation will be available after server starts: http://localhost:8000/docs
echo.
echo [MCP] MCP Tools available after starting stdio server
echo [MONITOR] Use monitor_cursor.bat to debug Cursor integration issues
echo.
pause
