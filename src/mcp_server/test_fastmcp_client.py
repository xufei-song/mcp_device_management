#!/usr/bin/env python3
"""
FastMCP测试客户端
用于测试FastMCP服务器的工具和提示功能
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FastMCPTestClient:
    """FastMCP测试客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
    async def test_tool(self, message: str = "Hello from test client") -> Dict[str, Any]:
        """测试工具调用"""
        try:
            async with aiohttp.ClientSession() as session:
                # 构造工具调用请求
                tool_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "test_tool",
                        "arguments": {
                            "message": message
                        }
                    }
                }
                
                logger.info(f"[测试工具] 发送请求: {message}")
                
                async with session.post(
                    f"{self.base_url}/mcp",
                    json=tool_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    result = await response.json()
                    logger.info(f"[测试工具] 收到响应: {result}")
                    return result
                    
        except Exception as e:
            logger.error(f"[测试工具] 错误: {str(e)}")
            return {"error": str(e)}
    
    async def test_prompt(self, topic: str = "FastMCP客户端测试", context: str = "自动化测试") -> Dict[str, Any]:
        """测试提示调用"""
        try:
            async with aiohttp.ClientSession() as session:
                # 构造提示请求
                prompt_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "prompts/get",
                    "params": {
                        "name": "test_prompt",
                        "arguments": {
                            "topic": topic,
                            "context": context
                        }
                    }
                }
                
                logger.info(f"[测试提示] 发送请求 - 主题: {topic}")
                
                async with session.post(
                    f"{self.base_url}/mcp",
                    json=prompt_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    result = await response.json()
                    logger.info(f"[测试提示] 收到响应")
                    return result
                    
        except Exception as e:
            logger.error(f"[测试提示] 错误: {str(e)}")
            return {"error": str(e)}
    
    async def test_server_info(self) -> Dict[str, Any]:
        """测试服务器信息"""
        try:
            async with aiohttp.ClientSession() as session:
                # 构造初始化请求
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "FastMCP Test Client",
                            "version": "1.0.0"
                        }
                    }
                }
                
                logger.info("[服务器信息] 发送初始化请求")
                
                async with session.post(
                    f"{self.base_url}/mcp",
                    json=init_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    result = await response.json()
                    logger.info(f"[服务器信息] 收到响应")
                    return result
                    
        except Exception as e:
            logger.error(f"[服务器信息] 错误: {str(e)}")
            return {"error": str(e)}
    
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("FastMCP测试客户端开始测试")
        logger.info("=" * 60)
        
        # 测试服务器信息
        logger.info("1. 测试服务器初始化...")
        server_info = await self.test_server_info()
        print(f"服务器信息: {json.dumps(server_info, ensure_ascii=False, indent=2)}")
        
        # 测试工具调用
        logger.info("\n2. 测试工具调用...")
        tool_result = await self.test_tool("这是来自测试客户端的消息")
        print(f"工具结果: {json.dumps(tool_result, ensure_ascii=False, indent=2)}")
        
        # 测试提示调用
        logger.info("\n3. 测试提示调用...")
        prompt_result = await self.test_prompt("设备管理", "MCP服务器测试环境")
        print(f"提示结果: {json.dumps(prompt_result, ensure_ascii=False, indent=2)}")
        
        logger.info("\n" + "=" * 60)
        logger.info("FastMCP测试客户端测试完成")
        logger.info("=" * 60)


async def main():
    """主函数"""
    try:
        # 创建测试客户端
        client = FastMCPTestClient()
        
        # 运行所有测试
        await client.run_all_tests()
        
    except Exception as e:
        logger.error(f"测试客户端运行错误: {str(e)}")


if __name__ == "__main__":
    # 运行测试客户端
    asyncio.run(main())
