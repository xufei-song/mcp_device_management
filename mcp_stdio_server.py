#!/usr/bin/env python3
"""
MCP stdio服务器 - 专门为Cursor集成设计
支持标准MCP协议：initialize, tools/list, tools/call, resources/list, prompts/list
"""

import json
import sys
import os
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mcp.protocol import MCPProtocol
from src.device.manager import DeviceManager

# 配置日志
log_dir = Path.cwd() / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"mcp_stdio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self):
        self.device_manager = DeviceManager()
        self.protocol = MCPProtocol(self.device_manager)
        self.initialized = False
        logger.info("MCP服务器初始化完成")
    
    def log_message(self, message_type, message_data, is_request=True):
        """记录MCP消息"""
        direction = "→" if is_request else "←"
        logger.info(f"{direction} {message_type}: {json.dumps(message_data, ensure_ascii=False)}")
    
    async def handle_message(self, message):
        """处理MCP消息"""
        try:
            if not isinstance(message, dict):
                logger.error(f"无效消息格式: {type(message)}")
                return {"error": "Invalid message format"}
            
            message_type = message.get("method")
            message_id = message.get("id")
            
            if not message_type:
                logger.error(f"缺少method字段: {message}")
                return {"error": "Missing method field"}
            
            logger.info(f"收到消息: {message_type} (ID: {message_id})")
            self.log_message(message_type, message, is_request=True)
            
            # 处理不同类型的消息
            if message_type == "initialize":
                response = await self.handle_initialize(message)
            elif message_type == "tools/list":
                response = await self.handle_tools_list(message)
            elif message_type == "tools/call":
                response = await self.handle_tools_call(message)
            elif message_type == "resources/list":
                response = await self.handle_resources_list(message)
            elif message_type == "prompts/list":
                response = await self.handle_prompts_list(message)
            else:
                logger.warning(f"未知消息类型: {message_type}")
                response = {"error": f"Unknown method: {message_type}"}
            
            # 添加ID到响应
            if message_id is not None:
                response["id"] = message_id
            
            logger.info(f"响应消息: {message_type} (ID: {message_id})")
            self.log_message(message_type, response, is_request=False)
            
            return response
            
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}", exc_info=True)
            return {"error": f"Internal error: {str(e)}"}
    
    async def handle_initialize(self, message):
        """处理初始化请求"""
        logger.info("处理初始化请求")
        try:
            # 返回初始化响应
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "MCP Test Device Management System",
                    "version": "1.0.0"
                }
            }
            self.initialized = True
            logger.info("初始化成功")
            return {"result": result}
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return {"error": f"Initialization failed: {str(e)}"}
    
    async def handle_tools_list(self, message):
        """处理工具列表请求"""
        logger.info("处理工具列表请求")
        try:
            if not self.initialized:
                logger.warning("服务器未初始化，拒绝工具列表请求")
                return {"error": "Server not initialized"}
            
            tools = self.protocol.get_tools()
            result = {"tools": tools}
            logger.info(f"返回 {len(tools)} 个工具")
            return {"result": result}
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}")
            return {"error": f"Failed to list tools: {str(e)}"}
    
    async def handle_tools_call(self, message):
        """处理工具调用请求"""
        logger.info("处理工具调用请求")
        try:
            if not self.initialized:
                logger.warning("服务器未初始化，拒绝工具调用请求")
                return {"error": "Server not initialized"}
            
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"调用工具: {tool_name} 参数: {arguments}")
            
            result = self.protocol.call_tool(tool_name, arguments)
            logger.info(f"工具调用成功: {tool_name}")
            return {"result": result}
        except Exception as e:
            logger.error(f"工具调用失败: {e}")
            return {"error": f"Tool call failed: {str(e)}"}
    
    async def handle_resources_list(self, message):
        """处理资源列表请求"""
        logger.info("处理资源列表请求")
        try:
            if not self.initialized:
                logger.warning("服务器未初始化，拒绝资源列表请求")
                return {"error": "Server not initialized"}
            
            # 返回空资源列表
            result = {"resources": []}
            logger.info("返回空资源列表")
            return {"result": result}
        except Exception as e:
            logger.error(f"获取资源列表失败: {e}")
            return {"error": f"Failed to list resources: {str(e)}"}
    
    async def handle_prompts_list(self, message):
        """处理提示列表请求"""
        logger.info("处理提示列表请求")
        try:
            if not self.initialized:
                logger.warning("服务器未初始化，拒绝提示列表请求")
                return {"error": "Server not initialized"}
            
            # 返回空提示列表
            result = {"prompts": []}
            logger.info("返回空提示列表")
            return {"result": result}
        except Exception as e:
            logger.error(f"获取提示列表失败: {e}")
            return {"error": f"Failed to list prompts: {str(e)}"}
    
    def run(self):
        """运行MCP服务器"""
        logger.info("MCP服务器启动，等待消息...")
        logger.info(f"日志文件: {log_file}")
        
        try:
            while True:
                # 读取一行输入
                line = sys.stdin.readline()
                if not line:
                    logger.info("输入流结束，服务器退出")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析JSON消息
                    message = json.loads(line)
                    logger.info(f"解析消息成功: {len(line)} 字符")
                    
                    # 异步处理消息
                    response = asyncio.run(self.handle_message(message))
                    
                    # 输出响应
                    response_json = json.dumps(response, ensure_ascii=False)
                    print(response_json, flush=True)
                    logger.info(f"响应已发送: {len(response_json)} 字符")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}, 输入: {line}")
                    error_response = {
                        "error": f"Invalid JSON: {str(e)}",
                        "id": None
                    }
                    print(json.dumps(error_response), flush=True)
                    
                except Exception as e:
                    logger.error(f"处理消息时发生未预期错误: {e}", exc_info=True)
                    error_response = {
                        "error": f"Unexpected error: {str(e)}",
                        "id": None
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            logger.info("收到中断信号，服务器退出")
        except Exception as e:
            logger.error(f"服务器运行时发生错误: {e}", exc_info=True)
        finally:
            logger.info("MCP服务器已停止")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("MCP stdio服务器启动")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"Python路径: {sys.path}")
    logger.info("=" * 60)
    
    server = MCPServer()
    server.run()
