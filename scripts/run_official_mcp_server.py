#!/usr/bin/env python3
"""
启动官方MCP SDK实现的测试设备管理服务器
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# 检查是否在虚拟环境中
def check_virtual_env():
    """检查是否在虚拟环境中运行"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
        'VIRTUAL_ENV' in os.environ
    )
    
    if not in_venv:
        venv_path = project_root / "venv"
        if venv_path.exists():
            print("警告: 检测到虚拟环境但未激活")
            print(f"请先激活虚拟环境: {venv_path / 'Scripts' / 'activate.bat'}")
            print("或运行: scripts\\run_official_mcp_server.bat")
            return False
        else:
            print("警告: 未找到虚拟环境，请先运行 scripts\\setup.bat")
            return False
    
    return True

# 导入MCP服务器
try:
    from src.mcp_server.test_device_mangement_server import create_simple_http_server
except ImportError as e:
    print(f"错误: 无法导入MCP服务器模块: {e}")
    print("请确保已运行 scripts/setup.bat 安装所有依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/mcp_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("MCPServerLauncher")


def main():
    """启动MCP服务器主函数"""
    
    # 检查虚拟环境
    if not check_virtual_env():
        sys.exit(1)
    
    # 确保日志目录存在
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logger.info("="*60)
    logger.info("启动测试设备管理MCP服务器 (官方SDK版本)")
    logger.info("="*60)
    
    # 设置环境变量
    os.environ["PYTHONPATH"] = str(project_root)
    
    # 服务器配置
    host = "localhost"
    port = 8001
    
    logger.info(f"服务器配置:")
    logger.info(f"  主机: {host}")
    logger.info(f"  端口: {port}")
    logger.info(f"  MCP端点: http://{host}:{port}/mcp")
    logger.info(f"  项目根目录: {project_root}")
    
    try:
        # 导入uvicorn
        import uvicorn
        
        # 创建FastAPI应用
        logger.info("创建MCP HTTP服务器...")
        fastapi_app = create_simple_http_server()
        
        logger.info("服务器启动中...")
        logger.info("按 Ctrl+C 停止服务器")
        logger.info("-"*60)
        
        # 启动服务器
        uvicorn.run(
            fastapi_app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n收到停止信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)
    finally:
        logger.info("服务器已停止")


if __name__ == "__main__":
    main()
