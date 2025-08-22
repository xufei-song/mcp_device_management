#!/usr/bin/env python3
"""
MCP测试设备管理系统启动脚本
"""

import uvicorn
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查虚拟环境
    if not Path("venv").exists():
        print("❌ 错误: 虚拟环境不存在")
        print("💡 请先运行: scripts\\setup.bat")
        sys.exit(1)
    
    # 检查src目录
    if not Path("src").exists():
        print("❌ 错误: src目录不存在")
        print("💡 请先运行: scripts\\setup.bat")
        sys.exit(1)
    
    # 检查关键模块目录
    required_dirs = ["src/mcp", "src/device", "src/handlers", "src/utils"]
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ 错误: {dir_path} 目录不存在")
            print("💡 请先运行: scripts\\setup.bat")
            sys.exit(1)
    
    # 检查关键依赖
    try:
        import uvicorn
        print("✅ uvicorn 已安装")
    except ImportError:
        print("❌ 错误: uvicorn 未安装")
        print("💡 请先运行: scripts\\setup.bat")
        sys.exit(1)
    
    try:
        import fastapi
        print("✅ fastapi 已安装")
    except ImportError:
        print("❌ 错误: fastapi 未安装")
        print("💡 请先运行: scripts\\setup.bat")
        sys.exit(1)
    
    try:
        import pydantic
        print("✅ pydantic 已安装")
    except ImportError:
        print("❌ 错误: pydantic 未安装")
        print("💡 请先运行: scripts\\setup.bat")
        sys.exit(1)
    
    # 检查设备目录
    if not Path("Devices").exists():
        print("❌ 错误: Devices目录不存在")
        print("💡 请先运行: scripts\\setup.bat")
        sys.exit(1)
    
    # 检查配置文件
    if not Path("config/settings.yaml").exists():
        print("⚠️  警告: config/settings.yaml 不存在，将使用默认配置")
    
    print("✅ 环境检查通过")
    print()

if __name__ == "__main__":
    # 环境检查
    check_environment()
    
    # 配置参数
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 启动MCP测试设备管理系统...")
    print(f"📍 服务器地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 调试模式: {debug}")
    print(f"📁 设备目录: {Path.cwd() / 'Devices'}")
    print("-" * 50)
    
    try:
        # 启动服务器
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
