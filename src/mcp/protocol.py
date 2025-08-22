"""
MCP协议实现
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ..device.manager import DeviceManager
from ..device.models import (
    DeviceCreate, DeviceUpdate, DeviceBorrow, DeviceReturn, 
    DeviceSearch, SuccessResponse, ErrorResponse
)


class MCPProtocol:
    """MCP协议实现类"""
    
    def __init__(self, device_manager: DeviceManager):
        """
        初始化MCP协议
        
        Args:
            device_manager: 设备管理器实例
        """
        self.device_manager = device_manager
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用工具"""
        return [
            {
                "name": "device.list",
                "description": "列出所有可用设备",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "device.connect",
                "description": "连接指定设备",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "device.disconnect",
                "description": "断开指定设备连接",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "device.execute",
                "description": "在设备上执行命令",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "command": {"type": "string"}
                    },
                    "required": ["device_id", "command"]
                }
            },
            {
                "name": "device.upload",
                "description": "向设备上传文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "local_path": {"type": "string"},
                        "remote_path": {"type": "string"}
                    },
                    "required": ["device_id", "local_path", "remote_path"]
                }
            },
            {
                "name": "device.download",
                "description": "从设备下载文件",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "remote_path": {"type": "string"},
                        "local_path": {"type": "string"}
                    },
                    "required": ["device_id", "remote_path", "local_path"]
                }
            },
            {
                "name": "device.status",
                "description": "获取设备状态信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "device.borrow",
                "description": "借用设备",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "borrower": {"type": "string"},
                        "purpose": {"type": "string"},
                        "expected_return_date": {"type": "string"}
                    },
                    "required": ["device_id", "borrower", "purpose", "expected_return_date"]
                }
            },
            {
                "name": "device.return",
                "description": "归还设备",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "returner": {"type": "string"}
                    },
                    "required": ["device_id", "returner"]
                }
            },
            {
                "name": "device.info",
                "description": "获取设备详细信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "device.create",
                "description": "创建设备记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "sku": {"type": "string"},
                        "cpu_type": {"type": "string"},
                        "specs": {"type": "object"}
                    },
                    "required": ["device_id", "name", "type", "sku", "cpu_type"]
                }
            },
            {
                "name": "device.update",
                "description": "更新设备信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "updates": {"type": "object"}
                    },
                    "required": ["device_id", "updates"]
                }
            },
            {
                "name": "device.delete",
                "description": "删除设备记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"}
                    },
                    "required": ["device_id"]
                }
            },
            {
                "name": "device.search",
                "description": "搜索设备",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {"type": "object"}
                    },
                    "required": []
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用指定工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            if tool_name == "device.list":
                return self._device_list()
            elif tool_name == "device.connect":
                return self._device_connect(arguments)
            elif tool_name == "device.disconnect":
                return self._device_disconnect(arguments)
            elif tool_name == "device.execute":
                return self._device_execute(arguments)
            elif tool_name == "device.upload":
                return self._device_upload(arguments)
            elif tool_name == "device.download":
                return self._device_download(arguments)
            elif tool_name == "device.status":
                return self._device_status(arguments)
            elif tool_name == "device.borrow":
                return self._device_borrow(arguments)
            elif tool_name == "device.return":
                return self._device_return(arguments)
            elif tool_name == "device.info":
                return self._device_info(arguments)
            elif tool_name == "device.create":
                return self._device_create(arguments)
            elif tool_name == "device.update":
                return self._device_update(arguments)
            elif tool_name == "device.delete":
                return self._device_delete(arguments)
            elif tool_name == "device.search":
                return self._device_search(arguments)
            else:
                return self._create_error("UNKNOWN_TOOL", f"未知工具: {tool_name}")
        except Exception as e:
            return self._create_error("INTERNAL_ERROR", f"工具执行失败: {str(e)}")
    
    def _device_list(self) -> Dict[str, Any]:
        """列出所有设备"""
        devices = self.device_manager.list_devices()
        return {
            "devices": [
                {
                    "id": device.device_id,
                    "type": device.type,
                    "name": device.name,
                    "status": device.status,
                    "info": {
                        "model": device.specs.model,
                        "version": device.specs.version,
                        "manufacturer": device.specs.manufacturer
                    }
                }
                for device in devices
            ]
        }
    
    def _device_connect(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """连接设备"""
        device_id = arguments.get("device_id")
        if not device_id:
            return self._create_error("INVALID_PARAMETERS", "缺少device_id参数")
        
        device = self.device_manager.get_device(device_id)
        if not device:
            return self._create_error("DEVICE_NOT_FOUND", f"设备 {device_id} 未找到")
        
        # 这里应该实现实际的设备连接逻辑
        return {
            "success": True,
            "device_id": device_id
        }
    
    def _device_disconnect(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """断开设备连接"""
        device_id = arguments.get("device_id")
        if not device_id:
            return self._create_error("INVALID_PARAMETERS", "缺少device_id参数")
        
        # 这里应该实现实际的设备断开逻辑
        return {
            "success": True,
            "device_id": device_id
        }
    
    def _device_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """在设备上执行命令"""
        device_id = arguments.get("device_id")
        command = arguments.get("command")
        
        if not device_id or not command:
            return self._create_error("INVALID_PARAMETERS", "缺少device_id或command参数")
        
        device = self.device_manager.get_device(device_id)
        if not device:
            return self._create_error("DEVICE_NOT_FOUND", f"设备 {device_id} 未找到")
        
        # 这里应该实现实际的命令执行逻辑
        return {
            "success": True,
            "output": f"执行命令: {command}",
            "error": "",
            "device_id": device_id
        }
    
    def _device_upload(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """向设备上传文件"""
        device_id = arguments.get("device_id")
        local_path = arguments.get("local_path")
        remote_path = arguments.get("remote_path")
        
        if not all([device_id, local_path, remote_path]):
            return self._create_error("INVALID_PARAMETERS", "缺少必要参数")
        
        # 这里应该实现实际的文件上传逻辑
        return {
            "success": True,
            "local_path": local_path,
            "remote_path": remote_path,
            "device_id": device_id
        }
    
    def _device_download(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """从设备下载文件"""
        device_id = arguments.get("device_id")
        remote_path = arguments.get("remote_path")
        local_path = arguments.get("local_path")
        
        if not all([device_id, remote_path, local_path]):
            return self._create_error("INVALID_PARAMETERS", "缺少必要参数")
        
        # 这里应该实现实际的文件下载逻辑
        return {
            "success": True,
            "remote_path": remote_path,
            "local_path": local_path,
            "device_id": device_id
        }
    
    def _device_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取设备状态信息"""
        device_id = arguments.get("device_id")
        if not device_id:
            return self._create_error("INVALID_PARAMETERS", "缺少device_id参数")
        
        status = self.device_manager.get_device_status(device_id)
        if not status:
            return self._create_error("DEVICE_NOT_FOUND", f"设备 {device_id} 未找到")
        
        return status
    
    def _device_borrow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """借用设备"""
        try:
            borrow_data = DeviceBorrow(**arguments)
            device = self.device_manager.borrow_device(borrow_data)
            
            if not device:
                return self._create_error("DEVICE_BORROW_FAILED", "设备借用失败")
            
            return {
                "success": True,
                "device_id": device.device_id,
                "borrower": borrow_data.borrower,
                "borrow_date": datetime.now().isoformat(),
                "expected_return_date": borrow_data.expected_return_date.isoformat(),
                "purpose": borrow_data.purpose
            }
        except Exception as e:
            return self._create_error("INVALID_PARAMETERS", f"参数错误: {str(e)}")
    
    def _device_return(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """归还设备"""
        try:
            return_data = DeviceReturn(**arguments)
            device = self.device_manager.return_device(return_data)
            
            if not device:
                return self._create_error("DEVICE_RETURN_FAILED", "设备归还失败")
            
            return {
                "success": True,
                "device_id": device.device_id,
                "returner": return_data.returner,
                "return_date": datetime.now().isoformat(),
                "borrow_duration": "计算中..."  # 这里应该计算实际的借用时长
            }
        except Exception as e:
            return self._create_error("INVALID_PARAMETERS", f"参数错误: {str(e)}")
    
    def _device_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取设备详细信息"""
        device_id = arguments.get("device_id")
        if not device_id:
            return self._create_error("INVALID_PARAMETERS", "缺少device_id参数")
        
        device = self.device_manager.get_device(device_id)
        if not device:
            return self._create_error("DEVICE_NOT_FOUND", f"设备 {device_id} 未找到")
        
        return device.dict()
    
    def _device_create(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """创建设备记录"""
        try:
            device_data = DeviceCreate(**arguments)
            device = self.device_manager.create_device(device_data)
            
            if not device:
                return self._create_error("DEVICE_CREATE_FAILED", "设备创建失败")
            
            return {
                "success": True,
                "device_id": device.device_id,
                "message": "设备创建成功"
            }
        except Exception as e:
            return self._create_error("INVALID_PARAMETERS", f"参数错误: {str(e)}")
    
    def _device_update(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """更新设备信息"""
        device_id = arguments.get("device_id")
        updates = arguments.get("updates")
        
        if not device_id or not updates:
            return self._create_error("INVALID_PARAMETERS", "缺少必要参数")
        
        try:
            update_data = DeviceUpdate(**updates)
            device = self.device_manager.update_device(device_id, update_data)
            
            if not device:
                return self._create_error("DEVICE_UPDATE_FAILED", "设备更新失败")
            
            return {
                "success": True,
                "device_id": device.device_id,
                "message": "设备信息更新成功"
            }
        except Exception as e:
            return self._create_error("INVALID_PARAMETERS", f"参数错误: {str(e)}")
    
    def _device_delete(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """删除设备记录"""
        device_id = arguments.get("device_id")
        if not device_id:
            return self._create_error("INVALID_PARAMETERS", "缺少device_id参数")
        
        success = self.device_manager.delete_device(device_id)
        if not success:
            return self._create_error("DEVICE_DELETE_FAILED", "设备删除失败")
        
        return {
            "success": True,
            "device_id": device_id,
            "message": "设备删除成功"
        }
    
    def _device_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """搜索设备"""
        query = arguments.get("query")
        filters = arguments.get("filters")
        
        devices = self.device_manager.search_devices(query, filters)
        
        return {
            "devices": [
                {
                    "device_id": device.device_id,
                    "name": device.name,
                    "type": device.type,
                    "sku": device.sku,
                    "status": device.status
                }
                for device in devices
            ],
            "total": len(devices)
        }
    
    def _create_error(self, code: str, message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "error": {
                "code": code,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
