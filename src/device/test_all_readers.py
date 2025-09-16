#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV读取器测试脚本
测试所有设备CSV文件的读取功能
"""

import sys
from pathlib import Path

# 导入所有读取器
from android_reader import read_android_devices
from ios_reader import read_ios_devices
from windows_reader import read_windows_devices
from other_reader import read_other_devices
from records_reader import read_records


def test_all_readers():
    """测试所有CSV读取器"""
    
    print("🚀 开始测试所有CSV读取器...")
    print("=" * 60)
    
    readers = [
        ("Android设备", read_android_devices),
        ("iOS设备", read_ios_devices),
        ("Windows设备", read_windows_devices),
        ("其他设备", read_other_devices),
        ("记录", read_records)
    ]
    
    results = {}
    total_records = 0
    
    for name, reader_func in readers:
        print(f"\n📋 测试 {name} 读取器...")
        try:
            data = reader_func()
            record_count = len(data)
            results[name] = {"status": "✅ 成功", "count": record_count}
            total_records += record_count
            print(f"   状态: ✅ 成功读取 {record_count} 条记录")
            
        except Exception as e:
            results[name] = {"status": "❌ 失败", "error": str(e)}
            print(f"   状态: ❌ 失败 - {e}")
    
    # 显示汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    success_count = 0
    for name, result in results.items():
        status = result["status"]
        if "成功" in status:
            count = result["count"]
            print(f"{name:15} | {status} | {count:3d} 条记录")
            success_count += 1
        else:
            error = result.get("error", "未知错误")
            print(f"{name:15} | {status} | 错误: {error}")
    
    print("-" * 60)
    print(f"测试完成: {success_count}/{len(readers)} 个读取器成功")
    print(f"总记录数: {total_records} 条")
    
    if success_count == len(readers):
        print("🎉 所有CSV读取器测试通过！")
        return True
    else:
        print("⚠️  部分CSV读取器测试失败！")
        return False


if __name__ == "__main__":
    try:
        success = test_all_readers()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ 测试脚本执行失败: {e}")
        sys.exit(1)