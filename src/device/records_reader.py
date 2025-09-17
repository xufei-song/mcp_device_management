#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记录CSV文件读取器和记录管理器
"""

import csv
import os
from pathlib import Path
from datetime import datetime

# 导入其他设备读取器
from android_reader import read_android_devices
from ios_reader import read_ios_devices  
from windows_reader import read_windows_devices
from other_reader import read_other_devices


def read_records():
    """
    读取记录CSV文件
    
    Returns:
        list: 包含所有记录信息的列表
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
        UnicodeDecodeError: 编码错误时抛出
        Exception: 其他读取错误时抛出
    """
    try:
        # 获取项目根目录
        current_dir = Path(__file__).parent.parent.parent
        csv_file_path = current_dir / "Devices" / "records.csv"
        
        # 检查文件是否存在
        if not csv_file_path.exists():
            raise FileNotFoundError(f"记录CSV文件未找到: {csv_file_path}")
        
        records = []
        
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
                    records.append(row)
        
        print(f"✅ 记录CSV文件读取成功！")
        print(f"📁 文件路径: {csv_file_path}")
        print(f"📊 共读取到 {len(records)} 条记录")
        print(f"📋 字段列表: {', '.join(fieldnames)}")
        
        return records
        
    except FileNotFoundError as e:
        print(f"❌ 文件未找到错误: {e}")
        raise
    except UnicodeDecodeError as e:
        print(f"❌ 文件编码错误: {e}")
        print("💡 建议：请确保CSV文件使用UTF-8编码保存")
        raise
    except Exception as e:
        print(f"❌ 读取记录CSV文件失败: {e}")
        raise


def find_device_by_asset_number(asset_number):
    """
    根据资产编号在所有设备表中查找设备信息
    
    Args:
        asset_number (str): 资产编号
        
    Returns:
        tuple: (device_info, device_type) 设备信息和设备类型，未找到返回 (None, None)
    """
    if not asset_number or not asset_number.strip():
        raise ValueError("资产编号不能为空")
        
    asset_number = asset_number.strip()
    
    # 定义设备类型和对应的读取器
    device_readers = {
        'android': read_android_devices,
        'ios': read_ios_devices,
        'windows': read_windows_devices,
        'other': read_other_devices
    }
    
    # 在每个设备表中查找
    for device_type, reader in device_readers.items():
        try:
            devices = reader()
            for device in devices:
                # 检查资产编号字段
                if device.get('资产编号', '').strip() == asset_number:
                    print(f"✅ 在{device_type}设备表中找到资产编号 {asset_number}")
                    return device, device_type
        except Exception as e:
            print(f"⚠️ 读取{device_type}设备表时出错: {e}")
            continue
    
    print(f"❌ 未在任何设备表中找到资产编号: {asset_number}")
    return None, None


def add_borrow_record(asset_number, borrower, reason=""):
    """
    添加借用记录
    
    Args:
        asset_number (str): 资产编号
        borrower (str): 借用者
        reason (str): 借用原因（可选）
        
    Returns:
        bool: 是否成功添加记录
    """
    return _add_record(asset_number, borrower, "借用", reason)


def add_return_record(asset_number, borrower, reason=""):
    """
    添加归还记录
    
    Args:
        asset_number (str): 资产编号
        borrower (str): 借用者
        reason (str): 归还原因（可选）
        
    Returns:
        bool: 是否成功添加记录
    """
    return _add_record(asset_number, borrower, "归还", reason)


def _add_record(asset_number, borrower, status, reason=""):
    """
    内部函数：添加记录到records.csv
    
    Args:
        asset_number (str): 资产编号
        borrower (str): 借用者
        status (str): 状态（借用/归还）
        reason (str): 原因
        
    Returns:
        bool: 是否成功添加记录
    """
    try:
        # 参数验证
        if not asset_number or not asset_number.strip():
            raise ValueError("资产编号不能为空")
        if not borrower or not borrower.strip():
            raise ValueError("借用者不能为空")
        if status not in ["借用", "归还"]:
            raise ValueError("状态必须是'借用'或'归还'")
            
        asset_number = asset_number.strip()
        borrower = borrower.strip()
        reason = reason.strip()
        
        # 查找设备信息
        device_info, device_type = find_device_by_asset_number(asset_number)
        if not device_info:
            raise ValueError(f"未找到资产编号为 {asset_number} 的设备")
        
        # 准备记录数据
        current_date = datetime.now().strftime("%d/%m/%Y")
        device_name = device_info.get('设备名称', '')
        
        # 创建新记录
        new_record = {
            '创建日期': current_date,
            '借用者': borrower,
            '设备': device_name,
            '资产编号': asset_number,
            '状态': status,
            '原因': reason
        }
        
        # 获取records.csv文件路径
        current_dir = Path(__file__).parent.parent.parent
        csv_file_path = current_dir / "Devices" / "records.csv"
        
        # 确保目录存在
        csv_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查文件是否存在，如果不存在则创建带标题行的文件
        if not csv_file_path.exists():
            with open(csv_file_path, 'w', encoding='utf-8', newline='') as file:
                fieldnames = ['创建日期', '借用者', '设备', '资产编号', '状态', '原因']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
        # 追加新记录到文件
        with open(csv_file_path, 'a', encoding='utf-8', newline='') as file:
            fieldnames = ['创建日期', '借用者', '设备', '资产编号', '状态', '原因']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow(new_record)
        
        print(f"✅ 成功添加{status}记录:")
        print(f"   📅 日期: {current_date}")
        print(f"   👤 借用者: {borrower}")
        print(f"   📱 设备: {device_name}")
        print(f"   🏷️ 资产编号: {asset_number}")
        print(f"   📋 状态: {status}")
        if reason:
            print(f"   💬 原因: {reason}")
        
        # TODO: 这里可以添加更新设备状态的逻辑
        # 现在先只添加记录，设备状态更新需要修改原始CSV文件
        
        return True
        
    except Exception as e:
        print(f"❌ 添加{status}记录失败: {e}")
        return False


def update_device_status_in_csv(asset_number, new_status, new_borrower=""):
    """
    更新设备在原始CSV文件中的状态和借用者信息
    
    Args:
        asset_number (str): 资产编号
        new_status (str): 新状态（可用/正在使用/设备异常等）
        new_borrower (str): 新借用者（归还时为空）
        
    Returns:
        bool: 是否成功更新
    """
    try:
        # 先找到设备所在的文件
        device_info, device_type = find_device_by_asset_number(asset_number)
        if not device_info:
            raise ValueError(f"未找到资产编号为 {asset_number} 的设备")
        
        # 根据设备类型确定CSV文件路径
        current_dir = Path(__file__).parent.parent.parent
        csv_files = {
            'android': current_dir / "Devices" / "android_devices.csv",
            'ios': current_dir / "Devices" / "ios_devices.csv", 
            'windows': current_dir / "Devices" / "windows_devices.csv",
            'other': current_dir / "Devices" / "other_devices.csv"
        }
        
        csv_file_path = csv_files.get(device_type)
        if not csv_file_path or not csv_file_path.exists():
            raise ValueError(f"设备类型 {device_type} 对应的CSV文件不存在")
        
        # 读取原有数据
        rows = []
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            
            for row in reader:
                if row.get('资产编号', '').strip() == asset_number.strip():
                    # 更新找到的设备记录
                    row['设备状态'] = new_status
                    if new_borrower:
                        row['借用者'] = new_borrower
                    else:
                        row['借用者'] = ""  # 归还时清空借用者
                    print(f"✅ 找到并更新设备记录: {asset_number}")
                
                rows.append(row)
        
        # 写回更新后的数据
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ 成功更新设备状态:")
        print(f"   🏷️ 资产编号: {asset_number}")
        print(f"   📋 新状态: {new_status}")
        if new_borrower:
            print(f"   👤 新借用者: {new_borrower}")
        else:
            print(f"   👤 借用者: 已清空")
            
        return True
        
    except Exception as e:
        print(f"❌ 更新设备状态失败: {e}")
        return False


def borrow_device(asset_number, borrower, reason=""):
    """
    借用设备（完整流程：添加借用记录 + 更新设备状态）
    
    Args:
        asset_number (str): 资产编号
        borrower (str): 借用者
        reason (str): 借用原因
        
    Returns:
        bool: 是否成功
    """
    try:
        # 1. 添加借用记录
        if not add_borrow_record(asset_number, borrower, reason):
            return False
            
        # 2. 更新设备状态为"正在使用"
        if not update_device_status_in_csv(asset_number, "正在使用", borrower):
            print("⚠️ 记录已添加，但设备状态更新失败")
            return False
            
        print(f"🎉 设备借用成功完成！")
        return True
        
    except Exception as e:
        print(f"❌ 设备借用失败: {e}")
        return False


def return_device(asset_number, borrower, reason=""):
    """
    归还设备（完整流程：添加归还记录 + 更新设备状态）
    
    Args:
        asset_number (str): 资产编号  
        borrower (str): 归还者
        reason (str): 归还原因
        
    Returns:
        bool: 是否成功
    """
    try:
        # 1. 添加归还记录
        if not add_return_record(asset_number, borrower, reason):
            return False
            
        # 2. 更新设备状态为"可用"
        if not update_device_status_in_csv(asset_number, "可用", ""):
            print("⚠️ 记录已添加，但设备状态更新失败")
            return False
            
        print(f"🎉 设备归还成功完成！")
        return True
        
    except Exception as e:
        print(f"❌ 设备归还失败: {e}")
        return False


if __name__ == "__main__":
    try:
        # 测试读取记录
        print("=" * 60)
        print("🔧 测试记录读取功能")
        print("=" * 60)
        
        records = read_records()
        
        # 显示前3条记录作为示例
        if records:
            print(f"\n📝 前3条记录示例:")
            for i, record in enumerate(records[:3], 1):
                print(f"\n记录 {i}:")
                for key, value in record.items():
                    if value.strip():  # 只显示非空字段
                        print(f"  {key}: {value}")
        else:
            print("⚠️  未读取到任何记录")
        
        # 测试设备查找功能
        print("\n\n" + "=" * 60)
        print("🔍 测试设备查找功能")
        print("=" * 60)
        
        # 测试查找一个存在的资产编号
        test_asset = "18294886"  # SAMSUNG Tab S8的资产编号
        print(f"\n🔍 查找资产编号: {test_asset}")
        device_info, device_type = find_device_by_asset_number(test_asset)
        
        if device_info:
            print(f"✅ 找到设备:")
            print(f"   设备类型: {device_type}")
            print(f"   设备名称: {device_info.get('设备名称', 'N/A')}")
            print(f"   设备状态: {device_info.get('设备状态', 'N/A')}")
            print(f"   当前借用者: {device_info.get('借用者', 'N/A')}")
        
        # 测试新接口的使用示例
        print("\n\n" + "=" * 60)
        print("📚 新接口使用示例")
        print("=" * 60)
        print("\n💡 借用设备示例代码:")
        print("   borrow_device('18294886', 'test_user', '测试借用')")
        print("\n💡 归还设备示例代码:")
        print("   return_device('18294886', 'test_user', '测试归还')")
        print("\n💡 单独添加记录示例代码:")
        print("   add_borrow_record('18294886', 'test_user', '测试原因')")
        print("   add_return_record('18294886', 'test_user', '测试原因')")
        
        print(f"\n🎉 所有测试完成！")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        exit(1)