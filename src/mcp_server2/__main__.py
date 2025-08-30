"""
MCP服务器2模块入口
"""
import sys
from .server import main

if __name__ == "__main__":
    # 设置默认端口为8002
    if "--port" not in sys.argv:
        sys.argv.extend(["--port", "8002"])
    main()
