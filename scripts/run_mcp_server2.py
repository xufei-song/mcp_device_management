#!/usr/bin/env python3
"""
启动基于官方SDK StreamableHTTP的MCP服务器2
"""

import sys
import os
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_virtual_env():
    """检查虚拟环境是否激活"""
    if os.name == 'nt':  # Windows
        if not os.environ.get('VIRTUAL_ENV'):
            print("错误: 虚拟环境未激活")
            print("请运行: scripts\\activate.bat")
            return False
    return True

def main():
    """主函数"""
    if not check_virtual_env():
        sys.exit(1)
    
    try:
        # 设置项目根目录
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # 检查MCP SDK
        try:
            import mcp
            import mcp.server
            import mcp.types
            logger.info("MCP SDK已安装并可用")
        except ImportError as e:
            print(f"错误: MCP SDK未安装或不完整: {e}")
            print("请运行: pip install mcp")
            sys.exit(1)
        
        # 导入并启动服务器 - 使用模块方式
        logger.info("启动MCP服务器2 (官方SDK StreamableHTTP)")
        logger.info("端口: 8002")
        logger.info("端点: http://127.0.0.1:8002/mcp")
        logger.info("-" * 60)
        
        # 使用Python模块方式启动（相当于 python -m src.mcp_server2）
        import runpy
        
        # 启动服务器 - 使用模块运行方式
        original_argv = sys.argv
        try:
            sys.argv = ["__main__", "--port", "8002"]
            runpy.run_module("src.mcp_server2", run_name="__main__")
            return 0
        finally:
            sys.argv = original_argv
        
    except KeyboardInterrupt:
        logger.info("服务器已停止")
        return 0
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
