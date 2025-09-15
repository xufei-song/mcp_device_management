# MCP Device Management - Copilot Instructions

## Project Overview
This is a test device management system based on the Model Context Protocol (MCP) 2024-11-05 specification. It's designed to manage and track test devices, recording device information like SKU, serial number, borrowing status, etc.

## Architecture

### Key Components
1. **Device Management Core** (`src/device/`)
   - `models.py`: Defines data structures for devices, borrowing records, etc.
   - `manager.py`: Core logic for device CRUD operations

2. **MCP Server Implementations**
   - `src/mcp_server2/`: Official MCP SDK implementation (recommended)
   - `src/mcp_server/`: Alternative implementation

3. **Device Storage Structure**
   - Devices are stored as JSON files in a hierarchical structure:
   - `Devices/{Android|IOS|Windows}/{device_id}/device.json`

## Development Workflow

### Setup & Running
1. Setup environment: `scripts\setup.bat` (one-time setup)
2. Activate environment: `scripts\activate.bat`
3. Start MCP server: `scripts\run_mcp_server2.bat` (recommended)
   - Server runs at: http://127.0.0.1:8002/mcp

### MCP Integration
- **Transport Protocol**: HTTP Stream only (via official MCP Python SDK)
- **Server Address**: http://localhost:8001/mcp (fastmcp) or http://127.0.0.1:8002/mcp (recommended)
- **Connection**: Must be configured in Cursor at `~/.cursor/mcp.json`
- **Manual Start**: Server requires manual start, not auto-started by Cursor
- **Not Supported**: stdio, WebSocket or other transport methods

## Coding Patterns

### MCP Tools Implementation
```python
@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    # Tool implementation logic
    if name == "get_device_info":
        return await _handle_get_device_info(arguments, ctx)
    # ... other tools

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="tool_name",
            description="Tool description",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter"}
                }
            }
        )
    ]
```

### Device Management Pattern
```python
# Create or update a device
device_manager = DeviceManager()
device = device_manager.get_device("device-id")
# OR
device = device_manager.create_device(DeviceCreate(...))
# OR 
device = device_manager.update_device("device-id", DeviceUpdate(...))
```

## Key Device Operations

1. **Device Information**: SKU, serial number, status, specs, etc.
2. **Borrowing Workflow**: Borrow → Use → Return
3. **Status Tracking**: Available, borrowed, maintenance, offline

## Project Requirements

### Hard Requirements
- Must use official MCP Python SDK (github.com/modelcontextprotocol/python-sdk) for all MCP implementations
- Only HTTP Stream transport is supported (no stdio/WebSocket)
- All operations must have detailed logging
- Manual server startup only - server needs to be started manually, not auto-started in mcp.json
- All new tools and prompts must use official SDK's standard methods
- Strictly follow the official SDK's API design and best practices

### File Structure Conventions
- Device data stored as JSON files
- Device folder structure must follow `Devices/{type}/{id}/` pattern
- Each device has its own `device.json` file

## Common Tasks
- Adding new MCP tools: Extend `app.call_tool()` and `app.list_tools()`
- Adding new MCP prompts: Extend `app.get_prompt()` and `app.list_prompts()`
- Managing devices: Use `DeviceManager` methods in `src/device/manager.py`

## Troubleshooting
- Port conflicts: Edit `src/mcp_server2/server.py` or use `--port` parameter
- Cursor connectivity: Ensure server is running at http://127.0.0.1:8002/mcp
- Detailed logs are available in terminal output during server execution

## Server Features
- **Detailed Logging**: All MCP operations have detailed logs for debugging
- **MCP Protocol Support**: Full support for initialize, tools/list, tools/call, prompts/list, prompts/get
- **Error Handling**: Complete JSON-RPC 2.0 error handling
- **Standard Compliance**: Strict adherence to MCP 2024-11-05 specification
