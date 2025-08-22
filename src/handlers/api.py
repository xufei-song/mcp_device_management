"""
HTTP API请求处理器
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from ..device.manager import DeviceManager
from ..device.models import (
    DeviceCreate, DeviceUpdate, DeviceBorrow, DeviceReturn, 
    DeviceSearch, DeviceListResponse, DeviceSearchResponse
)
from ..mcp.protocol import MCPProtocol

# 创建路由器
router = APIRouter()

# 初始化设备管理器和MCP协议
device_manager = DeviceManager()
mcp_protocol = MCPProtocol(device_manager)


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T12:00:00Z",
        "version": "1.0.0"
    }


@router.get("/tools")
async def list_tools():
    """列出所有可用工具"""
    return mcp_protocol.get_tools()


@router.post("/tools/{tool_name}/call")
async def call_tool(tool_name: str, request: Request):
    """调用指定工具"""
    try:
        arguments = await request.json()
        result = mcp_protocol.call_tool(tool_name, arguments)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 设备管理接口
@router.get("/tools/device.list")
async def list_devices():
    """列出所有设备"""
    devices = device_manager.list_devices()
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


@router.post("/tools/device.connect")
async def connect_device(request: Request):
    """连接设备"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少device_id参数")
        
        device = device_manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 未找到")
        
        # 这里应该实现实际的设备连接逻辑
        return {
            "success": True,
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.disconnect")
async def disconnect_device(request: Request):
    """断开设备连接"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少device_id参数")
        
        # 这里应该实现实际的设备断开逻辑
        return {
            "success": True,
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.execute")
async def execute_command(request: Request):
    """在设备上执行命令"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        command = data.get("command")
        
        if not device_id or not command:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        device = device_manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 未找到")
        
        # 这里应该实现实际的命令执行逻辑
        return {
            "success": True,
            "output": f"执行命令: {command}",
            "error": "",
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.upload")
async def upload_file(request: Request):
    """向设备上传文件"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        local_path = data.get("local_path")
        remote_path = data.get("remote_path")
        
        if not all([device_id, local_path, remote_path]):
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        # 这里应该实现实际的文件上传逻辑
        return {
            "success": True,
            "local_path": local_path,
            "remote_path": remote_path,
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.download")
async def download_file(request: Request):
    """从设备下载文件"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        remote_path = data.get("remote_path")
        local_path = data.get("local_path")
        
        if not all([device_id, remote_path, local_path]):
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        # 这里应该实现实际的文件下载逻辑
        return {
            "success": True,
            "remote_path": remote_path,
            "local_path": local_path,
            "device_id": device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.status")
async def get_device_status(request: Request):
    """获取设备状态信息"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少device_id参数")
        
        status = device_manager.get_device_status(device_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 未找到")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.info")
async def get_device_info(request: Request):
    """获取设备详细信息"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少device_id参数")
        
        device = device_manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"设备 {device_id} 未找到")
        
        return device.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.borrow")
async def borrow_device(request: Request):
    """借用设备"""
    try:
        data = await request.json()
        borrow_data = DeviceBorrow(**data)
        
        device = device_manager.borrow_device(borrow_data)
        if not device:
            raise HTTPException(status_code=400, detail="设备借用失败")
        
        return {
            "success": True,
            "device_id": device.device_id,
            "borrower": borrow_data.borrower,
            "borrow_date": "2024-01-01T12:00:00Z",
            "expected_return_date": borrow_data.expected_return_date.isoformat(),
            "purpose": borrow_data.purpose
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")


@router.post("/tools/device.return")
async def return_device(request: Request):
    """归还设备"""
    try:
        data = await request.json()
        return_data = DeviceReturn(**data)
        
        device = device_manager.return_device(return_data)
        if not device:
            raise HTTPException(status_code=400, detail="设备归还失败")
        
        return {
            "success": True,
            "device_id": device.device_id,
            "returner": return_data.returner,
            "return_date": "2024-01-01T18:00:00Z",
            "borrow_duration": "6h 0m"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")


@router.post("/tools/device.create")
async def create_device(request: Request):
    """创建设备记录"""
    try:
        data = await request.json()
        device_data = DeviceCreate(**data)
        
        device = device_manager.create_device(device_data)
        if not device:
            raise HTTPException(status_code=400, detail="设备创建失败")
        
        return {
            "success": True,
            "device_id": device.device_id,
            "message": "设备创建成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")


@router.post("/tools/device.update")
async def update_device(request: Request):
    """更新设备信息"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        updates = data.get("updates")
        
        if not device_id or not updates:
            raise HTTPException(status_code=400, detail="缺少必要参数")
        
        update_data = DeviceUpdate(**updates)
        device = device_manager.update_device(device_id, update_data)
        
        if not device:
            raise HTTPException(status_code=400, detail="设备更新失败")
        
        return {
            "success": True,
            "device_id": device.device_id,
            "message": "设备信息更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"参数错误: {str(e)}")


@router.post("/tools/device.delete")
async def delete_device(request: Request):
    """删除设备记录"""
    try:
        data = await request.json()
        device_id = data.get("device_id")
        
        if not device_id:
            raise HTTPException(status_code=400, detail="缺少device_id参数")
        
        success = device_manager.delete_device(device_id)
        if not success:
            raise HTTPException(status_code=400, detail="设备删除失败")
        
        return {
            "success": True,
            "device_id": device_id,
            "message": "设备删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/device.search")
async def search_devices(request: Request):
    """搜索设备"""
    try:
        data = await request.json()
        query = data.get("query")
        filters = data.get("filters")
        
        devices = device_manager.search_devices(query, filters)
        
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
