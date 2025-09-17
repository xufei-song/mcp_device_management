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

REM Check Azure CLI installation
echo [INFO] Checking Azure CLI installation...
where az >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Azure CLI not found. Please install Azure CLI first:
    echo [INFO] Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
    echo [INFO] Or install via winget: winget install -e --id Microsoft.AzureCLI
    echo [INFO] Script will continue, but Azure functions may not work
    echo.
) else (
    echo [SUCCESS] Azure CLI found
)

REM Create virtual environment
echo [INFO] Starting virtual environment creation...
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
pip install aiohttp
pip install aiofiles
pip install pyyaml
pip install jinja2
pip install python-multipart
pip install fastapi
pip install uvicorn
pip install azure-devops msrest

REM Install official MCP Python SDK
echo [INFO] Installing official MCP Python SDK...
pip install mcp

REM Install FastMCP library for MCP server development (optional)
echo [INFO] Installing FastMCP library...
pip install fastmcp

REM Install Azure dependencies for az_info scripts
echo [INFO] Installing Azure dependencies...
pip install azure-devops
pip install msrest

REM Create necessary directories
echo [INFO] Creating project directories...
if not exist "src" mkdir src
if not exist "src\mcp_server" mkdir src\mcp_server
if not exist "src\device" mkdir src\device
if not exist "src\handlers" mkdir src\handlers
if not exist "src\utils" mkdir src\utils
if not exist "config" mkdir config
if not exist ".vscode" mkdir .vscode

REM Create __init__.py files
echo [INFO] Creating Python package files...
if not exist "src\__init__.py" type nul > src\__init__.py
if not exist "src\mcp_server\__init__.py" type nul > src\mcp_server\__init__.py
if not exist "src\device\__init__.py" type nul > src\device\__init__.py
if not exist "src\handlers\__init__.py" type nul > src\handlers\__init__.py
if not exist "src\utils\__init__.py" type nul > src\utils\__init__.py
if not exist "tests\__init__.py" type nul > tests\__init__.py

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

echo.
echo [SUCCESS] Setup completed!
echo.
echo [NEXT] Next steps:
echo 1. Environment file created: .env (from env.template)
echo 2. Configuration file ready: config\settings.yaml
echo 4. Start MCP HTTP server: scripts\run_mcp_server.bat
echo 7. Run tests: scripts\run_tests.bat
echo.
echo [DOCS] View development documentation: DEVELOPMENT_GUIDE.md
echo [API] API documentation will be available after server starts: http://localhost:8000/docs
echo.
echo [MCP] MCP Tools available after starting stdio server
echo [FASTMCP] FastMCP library installed for simplified MCP server development
echo.
pause
