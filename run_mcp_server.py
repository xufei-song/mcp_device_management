#!/usr/bin/env python3
"""
MCP Streamable HTTP 服务器启动脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入并运行MCP服务器
from mcp.streamable_http_server import app
import uvicorn

if __name__ == "__main__":
    print("启动 MCP Streamable HTTP 服务器...")
    print("服务器地址: http://127.0.0.1:8000")
    print("按 Ctrl+C 停止服务器")
    print()
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
