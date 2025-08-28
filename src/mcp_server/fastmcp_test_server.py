#!/usr/bin/env python3
"""
FastMCP测试服务器
使用标准的MCP协议实现，不依赖第三方FastMCP库
支持HTTP Stream接口
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
import httpx

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class MCPPrompt:
    """MCP提示定义"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]

class SimpleMCPServer:
    """简单的MCP服务器实现"""
    
    def __init__(self, name: str = "TestDeviceManagement"):
        self.name = name
        self.tools: Dict[str, MCPTool] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        self.tool_handlers = {}
        self.prompt_handlers = {}
        self.app = FastAPI(title=f"{name} MCP Server")
        self._setup_routes()
        self._setup_builtin_tools_and_prompts()
    
    def _setup_routes(self):
        """设置FastAPI路由"""
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request: Request):
            """处理MCP请求"""
            try:
                data = await request.json()
                logger.info(f"[MCP] 收到请求: {data}")
                
                method = data.get("method")
                params = data.get("params", {})
                request_id = data.get("id")
                
                if method == "initialize":
                    response = await self._handle_initialize(params)
                elif method == "tools/list":
                    response = await self._handle_tools_list()
                elif method == "tools/call":
                    response = await self._handle_tool_call(params)
                elif method == "prompts/list":
                    response = await self._handle_prompts_list()
                elif method == "prompts/get":
                    response = await self._handle_prompt_get(params)
                else:
                    response = {
                        "error": {
                            "code": -32601,
                            "message": f"未知方法: {method}"
                        }
                    }
                
                result = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    **response
                }
                
                logger.info(f"[MCP] 发送响应: {result}")
                return JSONResponse(content=result)
                
            except Exception as e:
                logger.error(f"[MCP] 处理请求时出错: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id") if 'data' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"内部服务器错误: {str(e)}"
                    }
                }
                return JSONResponse(content=error_response, status_code=500)
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": "1.0.0"
                }
            }
        }
    
    async def _handle_tools_list(self) -> Dict[str, Any]:
        """处理工具列表请求"""
        tools_list = []
        for tool in self.tools.values():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {
            "result": {
                "tools": tools_list
            }
        }
    
    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tool_handlers:
            return {
                "error": {
                    "code": -32602,
                    "message": f"未找到工具: {tool_name}"
                }
            }
        
        try:
            handler = self.tool_handlers[tool_name]
            result = await handler(**arguments)
            
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"工具执行失败: {str(e)}"
                }
            }
    
    async def _handle_prompts_list(self) -> Dict[str, Any]:
        """处理提示列表请求"""
        prompts_list = []
        for prompt in self.prompts.values():
            prompts_list.append({
                "name": prompt.name,
                "description": prompt.description,
                "arguments": prompt.arguments
            })
        
        return {
            "result": {
                "prompts": prompts_list
            }
        }
    
    async def _handle_prompt_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理获取提示请求"""
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name not in self.prompt_handlers:
            return {
                "error": {
                    "code": -32602,
                    "message": f"未找到提示: {prompt_name}"
                }
            }
        
        try:
            handler = self.prompt_handlers[prompt_name]
            result = await handler(**arguments)
            
            return {
                "result": {
                    "description": f"Generated prompt for {prompt_name}",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": result
                            }
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "error": {
                    "code": -32603,
                    "message": f"提示生成失败: {str(e)}"
                }
            }
    
    def add_tool(self, name: str, description: str, input_schema: Dict[str, Any], handler):
        """添加工具"""
        self.tools[name] = MCPTool(name, description, input_schema)
        self.tool_handlers[name] = handler
        logger.info(f"[工具] 注册工具: {name}")
    
    def add_prompt(self, name: str, description: str, arguments: List[Dict[str, Any]], handler):
        """添加提示"""
        self.prompts[name] = MCPPrompt(name, description, arguments)
        self.prompt_handlers[name] = handler
        logger.info(f"[提示] 注册提示: {name}")
    
    def _setup_builtin_tools_and_prompts(self):
        """设置内置工具和提示"""
        
        # 测试工具
        async def test_tool_handler(message: str = "Hello MCP") -> str:
            """测试工具处理器"""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = {
                "status": "success",
                "message": f"MCP测试工具收到消息: {message}",
                "timestamp": timestamp,
                "server_info": {
                    "name": "Simple MCP Test Server",
                    "version": "1.0.0"
                }
            }
            logger.info(f"[测试工具] 处理消息: {message}")
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        self.add_tool(
            name="test_tool",
            description="测试工具 - 返回带时间戳的测试消息",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "测试消息内容",
                        "default": "Hello MCP"
                    }
                }
            },
            handler=test_tool_handler
        )
        
        # 测试提示
        async def test_prompt_handler(topic: str = "MCP测试", context: str = "默认上下文") -> str:
            """测试提示处理器"""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            prompt_content = f"""# MCP测试提示

## 主题: {topic}
## 上下文: {context}
## 生成时间: {timestamp}

---

### 系统信息
- 服务器: Simple MCP Test Server v1.0.0
- 协议: HTTP Stream

### 提示内容
这是一个由MCP服务器生成的测试提示。你可以使用这个提示来:

1. 测试MCP连接功能
2. 验证提示生成能力
3. 检查HTTP Stream接口

### 下一步操作
- 可以调用 `test_tool` 工具进行功能测试
- 可以修改主题和上下文参数来生成不同的提示
- 可以检查服务器日志来监控运行状态

---
*由MCP测试服务器生成于 {timestamp}*"""
            
            logger.info(f"[测试提示] 生成提示 - 主题: {topic}, 上下文: {context}")
            return prompt_content
        
        self.add_prompt(
            name="test_prompt",
            description="测试提示 - 生成基于主题和上下文的提示内容",
            arguments=[
                {
                    "name": "topic",
                    "description": "提示主题",
                    "required": False
                },
                {
                    "name": "context", 
                    "description": "上下文信息",
                    "required": False
                }
            ],
            handler=test_prompt_handler
        )

    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "name": "Simple MCP Test Server",
            "version": "1.0.0",
            "transport": "HTTP",
            "tools": list(self.tools.keys()),
            "prompts": list(self.prompts.keys()),
            "status": "running"
        }

# 全局服务器实例
mcp_server = SimpleMCPServer("TestDeviceManagement")

async def start_server(host: str = "localhost", port: int = 8001):
    """启动服务器"""
    try:
        logger.info("=" * 60)
        logger.info("Simple MCP测试服务器")
        logger.info("=" * 60)
        
        # 显示服务器信息
        info = mcp_server.get_server_info()
        for key, value in info.items():
            logger.info(f"{key}: {value}")
        
        logger.info("=" * 60)
        logger.info(f"服务器地址: http://{host}:{port}")
        logger.info("MCP端点: /mcp")
        logger.info("按 Ctrl+C 停止服务器")
        logger.info("=" * 60)
        
        # 启动服务器
        config = uvicorn.Config(
            app=mcp_server.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"[错误] 服务器启动失败: {str(e)}")
        raise

async def main():
    """主函数"""
    try:
        await start_server(host="localhost", port=8001)
    except KeyboardInterrupt:
        logger.info("[停止] 收到停止信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"[错误] 服务器运行错误: {str(e)}")
    finally:
        logger.info("[完成] MCP测试服务器已停止")

if __name__ == "__main__":
    # 运行服务器
    asyncio.run(main())