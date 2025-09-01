"""
MCP服务器2模块入口
支持 python -m src.mcp_server2 方式启动
"""
import sys
from .server import main

if __name__ == "__main__":
    # 设置默认端口为8002
    if "--port" not in sys.argv:
        sys.argv.extend(["--port", "8002"])
    
    print("启动MCP服务器2 (模块方式)")
    print("端口: 8002")
    print("端点: http://127.0.0.1:8002/mcp")
    print("推荐使用: scripts\\run_mcp_server2.bat (包含环境检查)")
    print("-" * 50)
    
    main()
