#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows设备CSV文件读取器
"""

import csv
import os
from pathlib import Path


def read_windows_devices():
    """
    读取Windows设备CSV文件
    
    Returns:
        list: 包含所有Windows设备信息的列表
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
        UnicodeDecodeError: 编码错误时抛出
        Exception: 其他读取错误时抛出
    """
    try:
        # 获取项目根目录
        current_dir = Path(__file__).parent.parent.parent
        csv_file_path = current_dir / "Devices" / "windows_devices.csv"
        
        # 检查文件是否存在
        if not csv_file_path.exists():
            raise FileNotFoundError(f"Windows设备CSV文件未找到: {csv_file_path}")
        
        devices = []
        
        # 读取CSV文件
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # 验证是否有数据
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise Exception("CSV文件格式错误：未找到列标题")
            
            # 读取所有行
            for row_num, row in enumerate(reader, start=2):  # 从第2行开始计数（考虑标题行）
                if any(row.values()):  # 跳过空行
                    devices.append(row)
        
        print(f"✅ Windows设备CSV文件读取成功！")
        print(f"📁 文件路径: {csv_file_path}")
        print(f"📊 共读取到 {len(devices)} 条设备记录")
        print(f"📋 字段列表: {', '.join(fieldnames)}")
        
        return devices
        
    except FileNotFoundError as e:
        print(f"❌ 文件未找到错误: {e}")
        raise
    except UnicodeDecodeError as e:
        print(f"❌ 文件编码错误: {e}")
        print("💡 建议：请确保CSV文件使用UTF-8编码保存")
        raise
    except Exception as e:
        print(f"❌ 读取Windows设备CSV文件失败: {e}")
        raise


def get_all_architectures():
    """
    获取所有芯片架构列表
    
    Returns:
        list: 包含所有不同芯片架构的列表（去重）
        
    Raises:
        Exception: 读取文件或处理数据时的错误
    """
    try:
        devices = read_windows_devices()
        
        # 提取所有芯片架构，去重并过滤空值
        architectures = set()
        for device in devices:
            arch = device.get('芯片架构', '').strip()
            if arch:  # 只添加非空的架构
                architectures.add(arch)
        
        arch_list = sorted(list(architectures))  # 排序便于查看
        
        print(f"✅ 芯片架构列表获取成功！")
        print(f"📊 共发现 {len(arch_list)} 种不同的芯片架构")
        print(f"🔧 架构列表: {', '.join(arch_list)}")
        
        return arch_list
        
    except Exception as e:
        print(f"❌ 获取芯片架构列表失败: {e}")
        raise


def query_devices_by_architecture(architecture):
    """
    根据芯片架构查询设备
    
    Args:
        architecture (str): 要查询的芯片架构字符串
        
    Returns:
        list: 匹配指定芯片架构的设备列表
        
    Raises:
        ValueError: 架构参数为空时抛出
        Exception: 读取文件或处理数据时的错误
    """
    try:
        if not architecture or not architecture.strip():
            raise ValueError("芯片架构参数不能为空")
        
        architecture = architecture.strip()
        devices = read_windows_devices()
        
        # 筛选匹配的设备
        matching_devices = []
        for device in devices:
            device_arch = device.get('芯片架构', '').strip()
            if device_arch.lower() == architecture.lower():  # 不区分大小写匹配
                matching_devices.append(device)
        
        print(f"✅ 芯片架构查询完成！")
        print(f"🔍 查询架构: {architecture}")
        print(f"📊 找到 {len(matching_devices)} 台匹配的设备")
        
        # 显示匹配设备的基本信息
        if matching_devices:
            print(f"\n💻 匹配设备列表:")
            for i, device in enumerate(matching_devices, 1):
                device_name = device.get('设备名称', '未知设备')
                sku = device.get('SKU', '')
                status = device.get('设备状态', '未知状态')
                borrower = device.get('借用者', '无')
                asset_no = device.get('资产编号', '')
                
                print(f"\n设备 {i}:")
                print(f"  设备名称: {device_name}")
                if sku:
                    print(f"  SKU: {sku}")
                print(f"  设备状态: {status}")
                print(f"  借用者: {borrower}")
                if asset_no:
                    print(f"  资产编号: {asset_no}")
        else:
            print(f"⚠️  未找到使用 '{architecture}' 架构的设备")
        
        return matching_devices
        
    except ValueError as e:
        print(f"❌ 参数错误: {e}")
        raise
    except Exception as e:
        print(f"❌ 芯片架构查询失败: {e}")
        raise


if __name__ == "__main__":
    try:
        # 检查命令行参数
        import sys
        
        if len(sys.argv) > 1:
            # 如果有参数，执行相应的功能
            command = sys.argv[1].lower()
            
            if command == "arch" or command == "architectures":
                # 显示所有芯片架构
                print("🔧 获取所有芯片架构...")
                architectures = get_all_architectures()
                
            elif command == "query" and len(sys.argv) > 2:
                # 根据芯片架构查询设备
                architecture = sys.argv[2]
                print(f"🔍 查询芯片架构为 '{architecture}' 的设备...")
                devices = query_devices_by_architecture(architecture)
                
            else:
                print("❌ 无效的命令参数")
                print("📋 用法示例:")
                print("  python windows_reader.py                    # 显示所有Windows设备")
                print("  python windows_reader.py arch               # 显示所有芯片架构")
                print("  python windows_reader.py query x64          # 查询x64架构的设备")
                print("  python windows_reader.py query ARM64        # 查询ARM64架构的设备")
                exit(1)
        else:
            # 默认行为：显示所有设备
            devices = read_windows_devices()
            
            # 显示前3条记录作为示例
            if devices:
                print(f"\n💻 前3条设备记录示例:")
                for i, device in enumerate(devices[:3], 1):
                    print(f"\n设备 {i}:")
                    for key, value in device.items():
                        if value.strip():  # 只显示非空字段
                            print(f"  {key}: {value}")
            else:
                print("⚠️  未读取到任何设备记录")
            
            # 额外显示芯片架构统计
            print(f"\n🔧 芯片架构统计:")
            try:
                architectures = get_all_architectures()
            except:
                pass  # 如果获取架构失败，不影响主流程
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        exit(1)