"""
设备管理器测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from src.device.manager import DeviceManager
from src.device.models import DeviceCreate, DeviceSpecs, DeviceUpdate, DeviceBorrow, DeviceReturn


class TestDeviceManager:
    """设备管理器测试类"""
    
    @pytest.fixture
    def temp_devices_dir(self):
        """创建临时设备目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def device_manager(self, temp_devices_dir):
        """创建设备管理器实例"""
        return DeviceManager(temp_devices_dir)
    
    @pytest.fixture
    def sample_device_data(self):
        """示例设备数据"""
        return DeviceCreate(
            device_id="test-device-001",
            name="测试设备",
            type="android",
            sku="TEST-001",
            cpu_type="x86_64",
            specs=DeviceSpecs(
                model="Test Model",
                version="1.0",
                manufacturer="Test Manufacturer",
                memory="4GB",
                storage="32GB"
            )
        )
    
    def test_init(self, temp_devices_dir):
        """测试初始化"""
        manager = DeviceManager(temp_devices_dir)
        
        # 检查目录是否创建
        assert Path(temp_devices_dir).exists()
        assert (Path(temp_devices_dir) / "Android").exists()
        assert (Path(temp_devices_dir) / "IOS").exists()
        assert (Path(temp_devices_dir) / "Windows").exists()
    
    def test_create_device(self, device_manager, sample_device_data):
        """测试创建设备"""
        device = device_manager.create_device(sample_device_data)
        
        assert device is not None
        assert device.device_id == "test-device-001"
        assert device.name == "测试设备"
        assert device.type == "android"
        
        # 检查文件是否创建
        device_path = Path(device_manager.devices_root) / "android" / "test-device-001"
        assert device_path.exists()
        assert (device_path / "device.json").exists()
        assert (device_path / "logs").exists()
        assert (device_path / "files").exists()
    
    def test_get_device(self, device_manager, sample_device_data):
        """测试获取设备"""
        # 先创建设备
        created_device = device_manager.create_device(sample_device_data)
        assert created_device is not None
        
        # 获取设备
        retrieved_device = device_manager.get_device("test-device-001")
        assert retrieved_device is not None
        assert retrieved_device.device_id == "test-device-001"
        assert retrieved_device.name == "测试设备"
    
    def test_list_devices(self, device_manager, sample_device_data):
        """测试列出设备"""
        # 创建多个设备
        device1 = device_manager.create_device(sample_device_data)
        
        # 创建第二个设备
        device2_data = DeviceCreate(
            device_id="test-device-002",
            name="测试设备2",
            type="ios",
            sku="TEST-002",
            cpu_type="arm64",
            specs=DeviceSpecs(
                model="Test Model 2",
                version="2.0",
                manufacturer="Test Manufacturer 2",
                memory="8GB",
                storage="64GB"
            )
        )
        device2 = device_manager.create_device(device2_data)
        
        # 列出所有设备
        devices = device_manager.list_devices()
        assert len(devices) == 2
        
        device_ids = [d.device_id for d in devices]
        assert "test-device-001" in device_ids
        assert "test-device-002" in device_ids
    
    def test_update_device(self, device_manager, sample_device_data):
        """测试更新设备"""
        # 先创建设备
        device = device_manager.create_device(sample_device_data)
        assert device is not None
        
        # 更新设备
        updates = DeviceUpdate(
            name="更新后的设备名称",
            specs={"memory": "8GB"}
        )
        
        updated_device = device_manager.update_device("test-device-001", updates)
        assert updated_device is not None
        assert updated_device.name == "更新后的设备名称"
        assert updated_device.specs.memory == "8GB"
    
    def test_borrow_device(self, device_manager, sample_device_data):
        """测试借用设备"""
        # 先创建设备
        device = device_manager.create_device(sample_device_data)
        assert device is not None
        
        # 借用设备
        borrow_data = DeviceBorrow(
            device_id="test-device-001",
            borrower="张三",
            purpose="功能测试",
            expected_return_date=datetime.now() + timedelta(days=1)
        )
        
        borrowed_device = device_manager.borrow_device(borrow_data)
        assert borrowed_device is not None
        assert borrowed_device.status == "borrowed"
        assert borrowed_device.current_borrower == "张三"
        assert len(borrowed_device.borrow_history) == 1
    
    def test_return_device(self, device_manager, sample_device_data):
        """测试归还设备"""
        # 先创建设备并借用
        device = device_manager.create_device(sample_device_data)
        borrow_data = DeviceBorrow(
            device_id="test-device-001",
            borrower="张三",
            purpose="功能测试",
            expected_return_date=datetime.now() + timedelta(days=1)
        )
        borrowed_device = device_manager.borrow_device(borrow_data)
        
        # 归还设备
        return_data = DeviceReturn(
            device_id="test-device-001",
            returner="张三"
        )
        
        returned_device = device_manager.return_device(return_data)
        assert returned_device is not None
        assert returned_device.status == "available"
        assert returned_device.current_borrower is None
        assert returned_device.current_borrow_info is None
    
    def test_search_devices(self, device_manager, sample_device_data):
        """测试搜索设备"""
        # 创建多个设备
        device1 = device_manager.create_device(sample_device_data)
        
        device2_data = DeviceCreate(
            device_id="test-device-002",
            name="iOS测试设备",
            type="ios",
            sku="TEST-002",
            cpu_type="arm64",
            specs=DeviceSpecs(
                model="Test Model 2",
                version="2.0",
                manufacturer="Test Manufacturer 2",
                memory="8GB",
                storage="64GB"
            )
        )
        device2 = device_manager.create_device(device2_data)
        
        # 搜索Android设备
        android_devices = device_manager.search_devices(filters={"type": "android"})
        assert len(android_devices) == 1
        assert android_devices[0].type == "android"
        
        # 搜索iOS设备
        ios_devices = device_manager.search_devices(filters={"type": "ios"})
        assert len(ios_devices) == 1
        assert ios_devices[0].type == "ios"
        
        # 文本搜索
        test_devices = device_manager.search_devices(query="测试")
        assert len(test_devices) == 2
    
    def test_delete_device(self, device_manager, sample_device_data):
        """测试删除设备"""
        # 先创建设备
        device = device_manager.create_device(sample_device_data)
        assert device is not None
        
        # 删除设备
        success = device_manager.delete_device("test-device-001")
        assert success is True
        
        # 验证设备已删除
        deleted_device = device_manager.get_device("test-device-001")
        assert deleted_device is None


if __name__ == "__main__":
    pytest.main([__file__])
