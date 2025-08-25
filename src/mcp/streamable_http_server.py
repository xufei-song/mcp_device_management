"""
Streamable HTTP MCP 服务器实现
基于 MCP 规范 2025-06-18
"""

import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
try:
    import sse_starlette.sse as sse
except ImportError:
    # 如果没有安装sse-starlette，使用简单的SSE实现
    class SimpleSSE:
        @staticmethod
        def Event(data, event=None):
            return f"event: {event}\ndata: {data}\n\n" if event else f"data: {data}\n\n"
    sse = SimpleSSE()

# 配置日志，使用青色输出
class ColoredFormatter(logging.Formatter):
    """青色日志格式化器"""
    
    def format(self, record):
        # 青色 ANSI 代码
        cyan = '\033[36m'
        reset = '\033[0m'
        record.msg = f"{cyan}[MCP-SERVER] {record.msg}{reset}"
        return super().format(record)

# 设置日志
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class StreamableHTTPMCPServer:
    """Streamable HTTP MCP 服务器"""
    
    def __init__(self):
        self.app = FastAPI(title="MCP Streamable HTTP Server", version="1.0.0")
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.setup_routes()
        
        # 固定的工具列表
        self.tools = [
            {
                "name": "simple_tool_1",
                "description": "第一个简单工具",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "输入消息"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "simple_tool_2", 
                "description": "第二个简单工具",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "number": {
                            "type": "integer",
                            "description": "输入数字"
                        }
                    },
                    "required": ["number"]
                }
            }
        ]
        
        # 固定的提示列表
        self.prompts = [
            {
                "name": "simple_prompt_1",
                "description": "第一个简单提示",
                "arguments": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "主题"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "simple_prompt_2",
                "description": "第二个简单提示", 
                "arguments": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "问题"
                        }
                    },
                    "required": ["question"]
                }
            }
        ]
    
    def setup_routes(self):
        """设置路由"""
        
        @self.app.post("/mcp")
        async def handle_post(request: Request):
            """处理 POST 请求 - 发送消息到服务器"""
            logger.info("收到 POST 请求")
            
            # 验证 Origin 头（安全要求）
            origin = request.headers.get("origin")
            if origin and origin not in ["http://localhost:3000", "http://127.0.0.1:3000"]:
                logger.warning(f"拒绝来自 {origin} 的请求")
                raise HTTPException(status_code=403, detail="Origin not allowed")
            
            # 检查协议版本
            protocol_version = request.headers.get("mcp-protocol-version", "2025-06-18")
            logger.info(f"协议版本: {protocol_version}")
            
            # 检查会话ID
            session_id = request.headers.get("mcp-session-id")
            logger.info(f"会话ID: {session_id}")
            
            try:
                body = await request.json()
                logger.info(f"收到消息: {json.dumps(body, ensure_ascii=False, indent=2)}")
                
                method = body.get("method")
                message_id = body.get("id")
                
                if method == "initialize":
                    return await self.handle_initialize(body, session_id)
                elif method == "tools/list":
                    return await self.handle_tools_list(body, session_id)
                elif method == "tools/call":
                    return await self.handle_tools_call(body, session_id)
                elif method == "prompts/list":
                    return await self.handle_prompts_list(body, session_id)
                else:
                    logger.warning(f"未知方法: {method}")
                    return Response(
                        content=json.dumps({
                            "jsonrpc": "2.0",
                            "id": message_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }),
                        status_code=400,
                        media_type="application/json"
                    )
                    
            except Exception as e:
                logger.error(f"处理 POST 请求时出错: {e}")
                return Response(
                    content=json.dumps({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }),
                    status_code=400,
                    media_type="application/json"
                )
        
        @self.app.get("/mcp")
        async def handle_get(request: Request):
            """处理 GET 请求 - 建立 SSE 流"""
            logger.info("收到 GET 请求 - 建立 SSE 流")
            
            # 验证 Accept 头
            accept = request.headers.get("accept", "")
            if "text/event-stream" not in accept:
                logger.warning("客户端不支持 SSE")
                raise HTTPException(status_code=406, detail="SSE not supported")
            
            # 检查会话ID
            session_id = request.headers.get("mcp-session-id")
            logger.info(f"SSE 流会话ID: {session_id}")
            
            async def event_generator():
                """SSE 事件生成器"""
                try:
                    # 发送连接确认事件
                    event_data = json.dumps({
                        "jsonrpc": "2.0",
                        "method": "notifications/connection_established",
                        "params": {
                            "message": "SSE 连接已建立"
                        }
                    })
                    yield sse.Event(data=event_data, event="mcp_notification")
                    
                    # 保持连接活跃
                    while True:
                        await asyncio.sleep(30)  # 30秒心跳
                        heartbeat_data = json.dumps({
                            "jsonrpc": "2.0", 
                            "method": "notifications/heartbeat",
                            "params": {
                                "timestamp": datetime.now().isoformat()
                            }
                        })
                        yield sse.Event(data=heartbeat_data, event="mcp_heartbeat")
                        
                except Exception as e:
                    logger.error(f"SSE 流错误: {e}")
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*"
                }
            )
    
    async def handle_initialize(self, body: Dict[str, Any], session_id: Optional[str]) -> Response:
        """处理初始化请求"""
        logger.info("处理初始化请求")
        
        # 生成新的会话ID
        new_session_id = session_id or str(uuid.uuid4())
        
        # 存储会话信息
        self.sessions[new_session_id] = {
            "created_at": datetime.now().isoformat(),
            "protocol_version": body.get("params", {}).get("protocolVersion", "2025-06-18")
        }
        
        response_data = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {},
                    "prompts": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "TestDeviceManagementMCP",
                    "version": "1.0.0"
                }
            }
        }
        
        logger.info(f"初始化完成，会话ID: {new_session_id}")
        
        return Response(
            content=json.dumps(response_data, ensure_ascii=False),
            media_type="application/json",
            headers={
                "mcp-session-id": new_session_id,
                "access-control-allow-origin": "*",
                "access-control-allow-headers": "*"
            }
        )
    
    async def handle_tools_list(self, body: Dict[str, Any], session_id: Optional[str]) -> Response:
        """处理工具列表请求"""
        logger.info("处理工具列表请求")
        
        if not session_id or session_id not in self.sessions:
            logger.warning("无效的会话ID")
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        response_data = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": self.tools
            }
        }
        
        logger.info(f"返回 {len(self.tools)} 个工具")
        
        return Response(
            content=json.dumps(response_data, ensure_ascii=False),
            media_type="application/json"
        )
    
    async def handle_tools_call(self, body: Dict[str, Any], session_id: Optional[str]) -> Response:
        """处理工具调用请求"""
        logger.info("处理工具调用请求")
        
        if not session_id or session_id not in self.sessions:
            logger.warning("无效的会话ID")
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
        
        # 根据工具名称返回固定内容
        if tool_name == "simple_tool_1":
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": f"工具1执行结果: 收到消息 '{arguments.get('message', '')}'"
                    }
                ]
            }
        elif tool_name == "simple_tool_2":
            number = arguments.get("number", 0)
            result = {
                "content": [
                    {
                        "type": "text", 
                        "text": f"工具2执行结果: 输入数字 {number} 的平方是 {number ** 2}"
                    }
                ]
            }
        else:
            logger.warning(f"未知工具: {tool_name}")
            return Response(
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }),
                status_code=400,
                media_type="application/json"
            )
        
        response_data = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": result
        }
        
        logger.info(f"工具调用完成: {tool_name}")
        
        return Response(
            content=json.dumps(response_data, ensure_ascii=False),
            media_type="application/json"
        )
    
    async def handle_prompts_list(self, body: Dict[str, Any], session_id: Optional[str]) -> Response:
        """处理提示列表请求"""
        logger.info("处理提示列表请求")
        
        if not session_id or session_id not in self.sessions:
            logger.warning("无效的会话ID")
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        response_data = {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "prompts": self.prompts
            }
        }
        
        logger.info(f"返回 {len(self.prompts)} 个提示")
        
        return Response(
            content=json.dumps(response_data, ensure_ascii=False),
            media_type="application/json"
        )

# 创建服务器实例
mcp_server = StreamableHTTPMCPServer()
app = mcp_server.app

if __name__ == "__main__":
    import uvicorn
    logger.info("启动 MCP Streamable HTTP 服务器...")
    uvicorn.run(
        app,
        host="127.0.0.1",  # 只绑定到 localhost（安全要求）
        port=8000,
        log_level="info"
    )
