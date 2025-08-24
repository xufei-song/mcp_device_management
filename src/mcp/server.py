"""
MCP服务器实现
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from .protocol import MCPProtocol
from ..device.manager import DeviceManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MCPConnectionManager:
    """MCP连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_handlers: Dict[str, Callable] = {}
    
    async def connect(self, websocket: WebSocket):
        """建立新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        try:
            client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
        except:
            client_info = "unknown"
        logger.info(f"[MCP] 新连接建立 - 客户端: {client_info}, 当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            try:
                client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
            except:
                client_info = "unknown"
            logger.info(f"[MCP] 连接断开 - 客户端: {client_info}, 当前连接数: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息到所有连接"""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message, ensure_ascii=False)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"[MCP] 发送消息失败: {e}")
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """发送个人消息"""
        if websocket in self.active_connections:
            try:
                message_str = json.dumps(message, ensure_ascii=False)
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"[MCP] 发送个人消息失败: {e}")
                self.disconnect(websocket)


class MCPServer:
    """MCP服务器实现"""
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.protocol = MCPProtocol(device_manager)
        self.connection_manager = MCPConnectionManager()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        self.connection_manager.connection_handlers = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
            "resources/watch": self._handle_resources_watch,
            "resources/unwatch": self._handle_resources_unwatch,
            "prompts/list": self._handle_prompts_list,
            "prompts/create": self._handle_prompts_create,
            "prompts/update": self._handle_prompts_update,
            "prompts/delete": self._handle_prompts_delete,
        }
    
    async def handle_websocket(self, websocket: WebSocket):
        """处理WebSocket连接"""
        await self.connection_manager.connect(websocket)
        
        try:
            while True:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # 记录接收到的消息
                message_type = message.get("type", "unknown")
                message_id = message.get("id", "no-id")
                logger.info(f"[MCP] 收到消息 - 类型: {message_type}, ID: {message_id}, 内容: {json.dumps(message, ensure_ascii=False)}")
                
                # 处理消息
                response = await self._process_message(message)
                
                # 记录响应
                if response:
                    response_type = response.get("type", "unknown")
                    logger.info(f"[MCP] 发送响应 - 类型: {response_type}, ID: {message_id}")
                    await self.connection_manager.send_personal_message(response, websocket)
                    
        except WebSocketDisconnect:
            logger.info("[MCP] WebSocket连接断开")
            self.connection_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"[MCP] 处理消息时出错: {e}")
            error_response = self._create_error_response("INTERNAL_ERROR", str(e))
            await self.connection_manager.send_personal_message(error_response, websocket)
            self.connection_manager.disconnect(websocket)
    
    async def _process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理MCP消息"""
        try:
            message_type = message.get("type")
            message_id = message.get("id")
            
            if not message_type:
                return self._create_error_response("INVALID_MESSAGE", "缺少消息类型")
            
            # 查找处理器
            handler = self.connection_manager.connection_handlers.get(message_type)
            if not handler:
                return self._create_error_response("UNKNOWN_MESSAGE_TYPE", f"未知消息类型: {message_type}")
            
            # 调用处理器
            result = await handler(message)
            
            # 添加消息ID到响应
            if message_id:
                result["id"] = message_id
            
            return result
            
        except Exception as e:
            return self._create_error_response("INTERNAL_ERROR", f"处理消息失败: {str(e)}")
    
    async def _handle_initialize(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        logger.info(f"[MCP] 处理初始化请求 - 消息ID: {message.get('id', 'no-id')}")
        return {
            "type": "initialize",
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
    
    async def _handle_tools_list(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具列表请求"""
        logger.info(f"[MCP] 处理工具列表请求 - 消息ID: {message.get('id', 'no-id')}")
        tools = self.protocol.get_tools()
        logger.info(f"[MCP] 返回工具列表 - 工具数量: {len(tools)}")
        return {
            "type": "tools/list",
            "tools": tools
        }
    
    async def _handle_tools_call(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        tool_name = message.get("name")
        arguments = message.get("arguments", {})
        message_id = message.get("id", "no-id")
        
        logger.info(f"[MCP] 处理工具调用请求 - 工具: {tool_name}, 参数: {json.dumps(arguments, ensure_ascii=False)}, 消息ID: {message_id}")
        
        if not tool_name:
            logger.error(f"[MCP] 工具调用失败 - 缺少工具名称, 消息ID: {message_id}")
            return self._create_error_response("INVALID_PARAMETERS", "缺少工具名称")
        
        try:
            result = self.protocol.call_tool(tool_name, arguments)
            logger.info(f"[MCP] 工具调用成功 - 工具: {tool_name}, 消息ID: {message_id}")
            return {
                "type": "tools/call",
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"[MCP] 工具调用失败 - 工具: {tool_name}, 错误: {str(e)}, 消息ID: {message_id}")
            return self._create_error_response("TOOL_CALL_FAILED", f"工具调用失败: {str(e)}")
    
    async def _handle_resources_list(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理资源列表请求"""
        uri = message.get("uri", "mcp://test-devices/")
        message_id = message.get("id", "no-id")
        
        logger.info(f"[MCP] 处理资源列表请求 - URI: {uri}, 消息ID: {message_id}")
        
        if uri == "mcp://test-devices/":
            # 根资源
            resources = [
                {
                    "uri": "mcp://test-devices/devices",
                    "name": "Devices",
                    "description": "设备列表",
                    "mimeType": "application/json"
                },
                {
                    "uri": "mcp://test-devices/tools",
                    "name": "Tools",
                    "description": "可用工具",
                    "mimeType": "application/json"
                },
                {
                    "uri": "mcp://test-devices/status",
                    "name": "Status",
                    "description": "系统状态",
                    "mimeType": "application/json"
                }
            ]
            logger.info(f"[MCP] 返回根资源列表 - 资源数量: {len(resources)}")
        elif uri == "mcp://test-devices/devices":
            # 设备列表
            devices = self.device_manager.list_devices()
            resources = []
            
            for device in devices:
                resources.append({
                    "uri": f"mcp://test-devices/devices/{device.type}/{device.device_id}",
                    "name": device.name,
                    "description": f"{device.type} 设备 - {device.sku}",
                    "mimeType": "application/json"
                })
            logger.info(f"[MCP] 返回设备资源列表 - 设备数量: {len(resources)}")
        else:
            resources = []
            logger.info(f"[MCP] 未知URI请求 - URI: {uri}")
        
        return {
            "type": "resources/list",
            "resources": resources
        }
    
    async def _handle_resources_read(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理资源读取请求"""
        uri = message.get("uri")
        message_id = message.get("id", "no-id")
        
        logger.info(f"[MCP] 处理资源读取请求 - URI: {uri}, 消息ID: {message_id}")
        
        if not uri:
            logger.error(f"[MCP] 资源读取失败 - 缺少资源URI, 消息ID: {message_id}")
            return self._create_error_response("INVALID_PARAMETERS", "缺少资源URI")
        
        try:
            if uri.startswith("mcp://test-devices/devices/"):
                # 解析设备URI
                parts = uri.split("/")
                if len(parts) >= 6:
                    device_type = parts[4]
                    device_id = parts[5]
                    
                    logger.info(f"[MCP] 读取设备资源 - 类型: {device_type}, ID: {device_id}")
                    device = self.device_manager.get_device(device_id)
                    if device:
                        logger.info(f"[MCP] 设备资源读取成功 - 设备: {device_id}")
                        return {
                            "type": "resources/read",
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "application/json",
                                    "text": json.dumps(device.dict(), ensure_ascii=False, indent=2)
                                }
                            ]
                        }
                    else:
                        logger.error(f"[MCP] 设备资源未找到 - 设备: {device_id}")
                        return self._create_error_response("RESOURCE_NOT_FOUND", f"设备 {device_id} 未找到")
            
            logger.error(f"[MCP] 资源未找到 - URI: {uri}")
            return self._create_error_response("RESOURCE_NOT_FOUND", f"资源 {uri} 未找到")
            
        except Exception as e:
            logger.error(f"[MCP] 资源读取失败 - URI: {uri}, 错误: {str(e)}")
            return self._create_error_response("INTERNAL_ERROR", f"读取资源失败: {str(e)}")
    
    async def _handle_resources_watch(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理资源监听请求"""
        uri = message.get("uri")
        
        if not uri:
            return self._create_error_response("INVALID_PARAMETERS", "缺少资源URI")
        
        # 这里可以实现资源变化监听
        return {
            "type": "resources/watch",
            "uri": uri
        }
    
    async def _handle_resources_unwatch(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理资源取消监听请求"""
        uri = message.get("uri")
        
        if not uri:
            return self._create_error_response("INVALID_PARAMETERS", "缺少资源URI")
        
        return {
            "type": "resources/unwatch",
            "uri": uri
        }
    
    async def _handle_prompts_list(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理提示列表请求"""
        return {
            "type": "prompts/list",
            "prompts": []
        }
    
    async def _handle_prompts_create(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理提示创建请求"""
        return self._create_error_response("NOT_IMPLEMENTED", "提示功能暂未实现")
    
    async def _handle_prompts_update(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理提示更新请求"""
        return self._create_error_response("NOT_IMPLEMENTED", "提示功能暂未实现")
    
    async def _handle_prompts_delete(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理提示删除请求"""
        return self._create_error_response("NOT_IMPLEMENTED", "提示功能暂未实现")
    
    def _create_error_response(self, code: str, message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "type": "error",
            "error": {
                "code": code,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def broadcast_device_event(self, event_type: str, data: Dict[str, Any]):
        """广播设备事件"""
        logger.info(f"[MCP] 广播设备事件 - 类型: {event_type}, 数据: {json.dumps(data, ensure_ascii=False)}")
        event_message = {
            "type": "device_event",
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.connection_manager.broadcast(event_message)
    
    async def broadcast_system_event(self, event_type: str, data: Dict[str, Any]):
        """广播系统事件"""
        logger.info(f"[MCP] 广播系统事件 - 类型: {event_type}, 数据: {json.dumps(data, ensure_ascii=False)}")
        event_message = {
            "type": "system_event",
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.connection_manager.broadcast(event_message)
