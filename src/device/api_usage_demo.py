#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备借用/归还API使用演示脚本
演示新添加的record_reader.py借用/归还功能
"""

import sys
from pathlib import Path

# 确保能导入本地模块
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from records_reader import (
    borrow_device, 
    return_device, 
    find_device_by_asset_number,
    add_borrow_record,
    add_return_record,
    read_records
)


def demo_device_search():
    """演示设备查找功能"""
    print("🔍 演示：设备查找功能")
    print("=" * 50)
    
    # 查找几个不同类型的设备
    test_assets = [
        ("18294886", "Android设备 - SAMSUNG Tab S8"),
        ("E2505869", "Android设备 - Meta Quest 3"),
        ("18294824", "Android设备 - SAMSUNG Tab S9")
    ]
    
    for asset_number, description in test_assets:
        print(f"\n🔍 查找 {description}")
        print(f"   资产编号: {asset_number}")
        
        device_info, device_type = find_device_by_asset_number(asset_number)
        if device_info:
            print(f"   ✅ 找到设备:")
            print(f"      设备名称: {device_info.get('设备名称', 'N/A')}")
            print(f"      设备类型: {device_type}")
            print(f"      设备状态: {device_info.get('设备状态', 'N/A')}")
            print(f"      当前借用者: {device_info.get('借用者', 'N/A')}")
        else:
            print(f"   ❌ 未找到设备")


def demo_record_management():
    """演示记录管理功能"""
    print("\n\n📝 演示：记录管理功能")
    print("=" * 50)
    
    # 选择一个设备进行演示
    demo_asset = "18294886"  # SAMSUNG Tab S8
    demo_user = "demo_user"
    
    print(f"\n📱 演示设备: 资产编号 {demo_asset}")
    
    # 查看设备信息
    device_info, device_type = find_device_by_asset_number(demo_asset)
    if device_info:
        print(f"   设备名称: {device_info.get('设备名称', 'N/A')}")
        print(f"   当前状态: {device_info.get('设备状态', 'N/A')}")
    
    print(f"\n📝 演示1: 仅添加借用记录")
    success = add_borrow_record(demo_asset, demo_user, "API演示 - 借用记录")
    print(f"   结果: {'✅ 成功' if success else '❌ 失败'}")
    
    print(f"\n📝 演示2: 仅添加归还记录")
    success = add_return_record(demo_asset, demo_user, "API演示 - 归还记录")
    print(f"   结果: {'✅ 成功' if success else '❌ 失败'}")


def demo_full_workflow():
    """演示完整借用/归还工作流程"""
    print("\n\n🎯 演示：完整借用/归还工作流程")
    print("=" * 50)
    
    # 找一个可用的设备进行演示
    available_assets = ["18294824", "18294873", "E2505869"]  # 一些可能可用的设备
    
    demo_asset = None
    for asset in available_assets:
        device_info, _ = find_device_by_asset_number(asset)
        if device_info and device_info.get('设备状态', '').strip() == '可用':
            demo_asset = asset
            break
    
    if not demo_asset:
        print("❌ 未找到可用设备进行演示，跳过完整工作流程演示")
        return
    
    demo_user = "workflow_demo_user"
    
    print(f"\n📱 选择演示设备: 资产编号 {demo_asset}")
    device_info, _ = find_device_by_asset_number(demo_asset)
    print(f"   设备名称: {device_info.get('设备名称', 'N/A')}")
    print(f"   初始状态: {device_info.get('设备状态', 'N/A')}")
    
    print(f"\n🔄 步骤1: 借用设备")
    success = borrow_device(demo_asset, demo_user, "完整工作流程演示")
    if success:
        print(f"   ✅ 借用成功")
        
        # 验证状态
        updated_device, _ = find_device_by_asset_number(demo_asset)
        print(f"   📋 更新后状态: {updated_device.get('设备状态', 'N/A')}")
        print(f"   👤 当前借用者: {updated_device.get('借用者', 'N/A')}")
        
        print(f"\n🔄 步骤2: 归还设备")
        success = return_device(demo_asset, demo_user, "演示完成，归还设备")
        if success:
            print(f"   ✅ 归还成功")
            
            # 验证状态
            returned_device, _ = find_device_by_asset_number(demo_asset)
            print(f"   📋 最终状态: {returned_device.get('设备状态', 'N/A')}")
            print(f"   👤 借用者: {returned_device.get('借用者', 'N/A')}")
        else:
            print(f"   ❌ 归还失败")
    else:
        print(f"   ❌ 借用失败")


def demo_recent_records():
    """演示查看最近的记录"""
    print("\n\n📊 演示：查看最近的记录")
    print("=" * 50)
    
    try:
        records = read_records()
        
        # 显示最近5条记录
        recent_records = records[-5:] if len(records) >= 5 else records
        
        print(f"\n📝 最近 {len(recent_records)} 条记录:")
        for i, record in enumerate(recent_records, 1):
            print(f"\n记录 {i}:")
            print(f"   📅 日期: {record.get('创建日期', 'N/A')}")
            print(f"   👤 操作者: {record.get('借用者', 'N/A')}")
            print(f"   📱 设备: {record.get('设备', 'N/A')}")
            print(f"   🏷️ 资产编号: {record.get('资产编号', 'N/A')}")
            print(f"   📋 状态: {record.get('状态', 'N/A')}")
            if record.get('原因', ''):
                print(f"   💬 原因: {record.get('原因', 'N/A')}")
                
    except Exception as e:
        print(f"❌ 读取记录失败: {e}")


def main():
    """主演示函数"""
    print("🎯 设备借用/归还API使用演示")
    print("=" * 60)
    print("本演示展示src/device/records_reader.py中新增的API功能")
    print("=" * 60)
    
    try:
        # 演示1: 设备查找
        demo_device_search()
        
        # 演示2: 记录管理
        demo_record_management()
        
        # 演示3: 完整工作流程
        demo_full_workflow()
        
        # 演示4: 查看最近记录
        demo_recent_records()
        
        print("\n\n🎉 演示完成！")
        print("=" * 60)
        print("📚 主要API接口:")
        print("   • find_device_by_asset_number(asset_number)")
        print("   • borrow_device(asset_number, borrower, reason)")
        print("   • return_device(asset_number, borrower, reason)")
        print("   • add_borrow_record(asset_number, borrower, reason)")
        print("   • add_return_record(asset_number, borrower, reason)")
        print("   • read_records()")
        print("\n💡 更多详细信息请查看 src/device/README.md")
        
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 演示脚本执行失败: {e}")
        sys.exit(1)