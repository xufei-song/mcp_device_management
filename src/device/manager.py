"""
设备管理器核心类
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from .models import Device, DeviceCreate, DeviceUpdate, DeviceBorrow, DeviceReturn


class DeviceManager:
    """设备管理器"""
    
    def __init__(self, devices_root: str = "Devices"):
        """
        初始化设备管理器
        
        Args:
            devices_root: 设备根目录路径
        """
        self.devices_root = Path(devices_root)
        self.devices_root.mkdir(exist_ok=True)
        
        # 确保设备类型目录存在
        for device_type in ["Android", "IOS", "Windows"]:
            (self.devices_root / device_type).mkdir(exist_ok=True)
    
    def _get_device_path(self, device_id: str, device_type: str) -> Path:
        """获取设备目录路径"""
        return self.devices_root / device_type / device_id
    
    def _get_device_json_path(self, device_id: str, device_type: str) -> Path:
        """获取设备JSON文件路径"""
        return self._get_device_path(device_id, device_type) / "device.json"
    
    def _load_device(self, device_id: str, device_type: str) -> Optional[Device]:
        """从JSON文件加载设备信息"""
        json_path = self._get_device_json_path(device_id, device_type)
        if not json_path.exists():
            return None
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Device(**data)
        except Exception as e:
            print(f"加载设备 {device_id} 失败: {e}")
            return None
    
    def _save_device(self, device: Device) -> bool:
        """保存设备信息到JSON文件"""
        try:
            device_path = self._get_device_path(device.device_id, device.type)
            device_path.mkdir(exist_ok=True)
            
            # 创建子目录
            (device_path / "logs").mkdir(exist_ok=True)
            (device_path / "files").mkdir(exist_ok=True)
            
            json_path = device_path / "device.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(device.dict(), f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存设备 {device.device_id} 失败: {e}")
            return False
    
    def list_devices(self) -> List[Device]:
        """列出所有设备"""
        devices = []
        
        for device_type in ["Android", "IOS", "Windows"]:
            type_path = self.devices_root / device_type
            if not type_path.exists():
                continue
            
            for device_dir in type_path.iterdir():
                if device_dir.is_dir():
                    device = self._load_device(device_dir.name, device_type)
                    if device:
                        devices.append(device)
        
        return devices
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """获取指定设备信息"""
        # 遍历所有设备类型查找设备
        for device_type in ["Android", "IOS", "Windows"]:
            device = self._load_device(device_id, device_type)
            if device:
                return device
        return None
    
    def create_device(self, device_data: DeviceCreate) -> Optional[Device]:
        """创建设备"""
        # 检查设备是否已存在
        if self.get_device(device_data.device_id):
            return None
        
        # 创建设备对象
        device = Device(
            device_id=device_data.device_id,
            name=device_data.name,
            type=device_data.type,
            sku=device_data.sku,
            cpu_type=device_data.cpu_type,
            specs=device_data.specs,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # 保存设备信息
        if self._save_device(device):
            return device
        return None
    
    def update_device(self, device_id: str, updates: DeviceUpdate) -> Optional[Device]:
        """更新设备信息"""
        device = self.get_device(device_id)
        if not device:
            return None
        
        # 更新字段
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(device, field):
                setattr(device, field, value)
        
        device.last_updated = datetime.now()
        
        # 保存更新
        if self._save_device(device):
            return device
        return None
    
    def delete_device(self, device_id: str) -> bool:
        """删除设备"""
        device = self.get_device(device_id)
        if not device:
            return False
        
        try:
            device_path = self._get_device_path(device_id, device.type)
            if device_path.exists():
                import shutil
                shutil.rmtree(device_path)
                return True
        except Exception as e:
            print(f"删除设备 {device_id} 失败: {e}")
        
        return False
    
    def borrow_device(self, borrow_data: DeviceBorrow) -> Optional[Device]:
        """借用设备"""
        device = self.get_device(borrow_data.device_id)
        if not device:
            return None
        
        if device.status != "available":
            return None
        
        # 更新设备状态
        device.status = "borrowed"
        device.current_borrower = borrow_data.borrower
        device.current_borrow_info = {
            "borrower": borrow_data.borrower,
            "borrow_date": datetime.now(),
            "expected_return_date": borrow_data.expected_return_date,
            "purpose": borrow_data.purpose,
            "contact": borrow_data.contact
        }
        
        # 添加到借用历史
        device.borrow_history.append({
            "borrower": borrow_data.borrower,
            "borrow_date": datetime.now(),
            "return_date": None,
            "purpose": borrow_data.purpose,
            "contact": borrow_data.contact,
            "notes": None
        })
        
        device.last_updated = datetime.now()
        
        # 保存更新
        if self._save_device(device):
            return device
        return None
    
    def return_device(self, return_data: DeviceReturn) -> Optional[Device]:
        """归还设备"""
        device = self.get_device(return_data.device_id)
        if not device:
            return None
        
        if device.status != "borrowed":
            return None
        
        # 更新设备状态
        device.status = "available"
        device.current_borrower = None
        device.current_borrow_info = None
        
        # 更新借用历史记录
        if device.borrow_history:
            last_record = device.borrow_history[-1]
            if last_record.return_date is None:
                last_record.return_date = datetime.now()
        
        device.last_updated = datetime.now()
        
        # 保存更新
        if self._save_device(device):
            return device
        return None
    
    def search_devices(self, query: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Device]:
        """搜索设备"""
        devices = self.list_devices()
        
        if not query and not filters:
            return devices
        
        filtered_devices = []
        
        for device in devices:
            # 文本搜索
            if query:
                search_text = f"{device.name} {device.sku} {device.type} {device.cpu_type}".lower()
                if query.lower() not in search_text:
                    continue
            
            # 过滤条件
            if filters:
                match = True
                for key, value in filters.items():
                    if key == "type" and device.type.lower() != value.lower():
                        match = False
                        break
                    elif key == "status" and device.status != value:
                        match = False
                        break
                    elif key == "cpu_type" and device.cpu_type != value:
                        match = False
                        break
                    elif key == "available" and (value and device.status != "available"):
                        match = False
                        break
                
                if not match:
                    continue
            
            filtered_devices.append(device)
        
        return filtered_devices
    
    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """获取设备状态信息"""
        device = self.get_device(device_id)
        if not device:
            return None
        
        return {
            "device_id": device.device_id,
            "name": device.name,
            "type": device.type,
            "sku": device.sku,
            "cpu_type": device.cpu_type,
            "status": device.status,
            "current_borrower": device.current_borrower,
            "specs": device.specs.dict(),
            "borrow_history": device.borrow_history,
            "last_updated": device.last_updated.isoformat()
        }
