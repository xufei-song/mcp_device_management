"""
设备数据模型定义
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DeviceSpecs(BaseModel):
    """设备规格信息"""
    model: str = Field(..., description="设备型号")
    version: str = Field(..., description="系统版本")
    manufacturer: str = Field(..., description="制造商")
    memory: str = Field(..., description="内存大小")
    storage: str = Field(..., description="存储大小")
    screen_resolution: Optional[str] = Field(None, description="屏幕分辨率")
    battery_capacity: Optional[str] = Field(None, description="电池容量")


class BorrowRecord(BaseModel):
    """借用记录"""
    borrower: str = Field(..., description="借用者姓名")
    borrow_date: datetime = Field(..., description="借用开始时间")
    return_date: Optional[datetime] = Field(None, description="归还时间")
    purpose: str = Field(..., description="借用目的")
    contact: Optional[str] = Field(None, description="联系方式")
    notes: Optional[str] = Field(None, description="备注信息")


class CurrentBorrowInfo(BaseModel):
    """当前借用信息"""
    borrower: str = Field(..., description="借用者姓名")
    borrow_date: datetime = Field(..., description="借用开始时间")
    expected_return_date: datetime = Field(..., description="预期归还时间")
    purpose: str = Field(..., description="借用目的")
    contact: Optional[str] = Field(None, description="联系方式")


class MaintenanceRecord(BaseModel):
    """维护记录"""
    date: datetime = Field(..., description="维护日期")
    type: str = Field(..., description="维护类型: maintenance|repair|upgrade")
    description: str = Field(..., description="维护描述")
    technician: str = Field(..., description="技术人员")
    cost: float = Field(0.0, description="维护成本")


class Location(BaseModel):
    """设备位置信息"""
    building: Optional[str] = Field(None, description="建筑名称")
    floor: Optional[str] = Field(None, description="楼层")
    room: Optional[str] = Field(None, description="房间号")
    rack: Optional[str] = Field(None, description="机架位置")


class Device(BaseModel):
    """设备信息模型"""
    device_id: str = Field(..., description="设备唯一标识符")
    name: str = Field(..., description="设备显示名称")
    type: str = Field(..., description="设备类型: android|ios|windows")
    sku: str = Field(..., description="设备SKU编号")
    cpu_type: str = Field(..., description="CPU类型: x86_64|arm64|armv7")
    specs: DeviceSpecs = Field(..., description="设备规格信息")
    status: str = Field("available", description="设备状态: available|borrowed|maintenance|offline")
    current_borrower: Optional[str] = Field(None, description="当前借用者")
    current_borrow_info: Optional[CurrentBorrowInfo] = Field(None, description="当前借用信息")
    borrow_history: List[BorrowRecord] = Field(default_factory=list, description="借用历史记录")
    maintenance_history: List[MaintenanceRecord] = Field(default_factory=list, description="维护历史记录")
    location: Optional[Location] = Field(None, description="设备位置信息")
    tags: List[str] = Field(default_factory=list, description="设备标签")
    notes: Optional[str] = Field(None, description="设备备注信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    last_maintenance: Optional[datetime] = Field(None, description="最后维护时间")
    next_maintenance: Optional[datetime] = Field(None, description="下次维护时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeviceCreate(BaseModel):
    """创建设备请求模型"""
    device_id: str = Field(..., description="设备唯一标识符")
    name: str = Field(..., description="设备显示名称")
    type: str = Field(..., description="设备类型")
    sku: str = Field(..., description="设备SKU编号")
    cpu_type: str = Field(..., description="CPU类型")
    specs: DeviceSpecs = Field(..., description="设备规格信息")


class DeviceUpdate(BaseModel):
    """更新设备请求模型"""
    name: Optional[str] = Field(None, description="设备显示名称")
    specs: Optional[Dict[str, Any]] = Field(None, description="设备规格信息")
    location: Optional[Location] = Field(None, description="设备位置信息")
    tags: Optional[List[str]] = Field(None, description="设备标签")
    notes: Optional[str] = Field(None, description="设备备注信息")


class DeviceBorrow(BaseModel):
    """借用设备请求模型"""
    device_id: str = Field(..., description="设备ID")
    borrower: str = Field(..., description="借用者姓名")
    purpose: str = Field(..., description="借用目的")
    expected_return_date: datetime = Field(..., description="预期归还时间")
    contact: Optional[str] = Field(None, description="联系方式")


class DeviceReturn(BaseModel):
    """归还设备请求模型"""
    device_id: str = Field(..., description="设备ID")
    returner: str = Field(..., description="归还者姓名")


class DeviceSearch(BaseModel):
    """搜索设备请求模型"""
    query: Optional[str] = Field(None, description="搜索查询")
    filters: Optional[Dict[str, Any]] = Field(None, description="过滤条件")


class DeviceListResponse(BaseModel):
    """设备列表响应模型"""
    devices: List[Device] = Field(..., description="设备列表")
    total: int = Field(..., description="设备总数")


class DeviceSearchResponse(BaseModel):
    """设备搜索响应模型"""
    devices: List[Device] = Field(..., description="搜索结果")
    total: int = Field(..., description="结果总数")


class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field(..., description="响应消息")
    device_id: Optional[str] = Field(None, description="设备ID")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: Dict[str, Any] = Field(..., description="错误信息")
