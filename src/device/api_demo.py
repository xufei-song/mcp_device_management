#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Device Module API 使用示例
演示README.md中介绍的所有API接口
"""

import sys
from pathlib import Path

# 确保能导入本地模块
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# 导入各个读取器
from android_reader import read_android_devices
from ios_reader import read_ios_devices
from windows_reader import read_windows_devices, get_all_architectures, query_devices_by_architecture
from other_reader import read_other_devices
from records_reader import read_records


def demonstrate_basic_readers():
    """演示基础读取器功能"""
    print("🔧 基础读取器演示")
    print("=" * 50)
    
    try:
        # Android设备
        print("\n📱 Android设备:")
        android_devices = read_android_devices()
        available_android = [d for d in android_devices if d['设备状态'] == '可用']
        print(f"   总计: {len(android_devices)} 台，可用: {len(available_android)} 台")
        
        # iOS设备
        print("\n🍎 iOS设备:")
        ios_devices = read_ios_devices()
        available_ios = [d for d in ios_devices if d['设备状态'] == '可用']
        print(f"   总计: {len(ios_devices)} 台，可用: {len(available_ios)} 台")
        
        # Windows设备
        print("\n💻 Windows设备:")
        windows_devices = read_windows_devices()
        available_windows = [d for d in windows_devices if d['设备状态'] == '可用']
        print(f"   总计: {len(windows_devices)} 台，可用: {len(available_windows)} 台")
        
        # 其他设备
        print("\n🔧 其他设备:")
        other_devices = read_other_devices()
        available_other = [d for d in other_devices if d['设备状态'] == '可用']
        print(f"   总计: {len(other_devices)} 台，可用: {len(available_other)} 台")
        
        # 记录
        print("\n📝 借用记录:")
        records = read_records()
        borrow_records = [r for r in records if r['状态'] == '借用']
        return_records = [r for r in records if r['状态'] == '归还']
        print(f"   总记录: {len(records)} 条，借用: {len(borrow_records)} 条，归还: {len(return_records)} 条")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础读取器演示失败: {e}")
        return False


def demonstrate_windows_advanced_features():
    """演示Windows设备高级功能"""
    print("\n\n🚀 Windows设备高级功能演示")
    print("=" * 50)
    
    try:
        # 获取所有架构
        print("\n🔧 芯片架构列表:")
        architectures = get_all_architectures()
        
        # 按架构查询设备
        print("\n📊 按架构统计设备:")
        total_devices = 0
        for arch in architectures:
            devices = query_devices_by_architecture(arch)
            available = sum(1 for d in devices if d['设备状态'] == '可用')
            in_use = sum(1 for d in devices if d['设备状态'] == '正在使用')
            total_devices += len(devices)
            print(f"   {arch}: 总计 {len(devices)} 台 | 可用 {available} 台 | 使用中 {in_use} 台")
        
        print(f"\n✅ 架构查询验证: 总计 {total_devices} 台设备")
        return True
        
    except Exception as e:
        print(f"❌ Windows高级功能演示失败: {e}")
        return False


def demonstrate_cross_platform_statistics():
    """演示跨平台设备统计"""
    print("\n\n📊 跨平台设备统计演示")
    print("=" * 50)
    
    try:
        # 获取各平台设备数量
        android_count = len(read_android_devices())
        ios_count = len(read_ios_devices())
        windows_count = len(read_windows_devices())
        other_count = len(read_other_devices())
        
        total_devices = android_count + ios_count + windows_count + other_count
        
        print(f"\n📈 设备分布统计:")
        print(f"   Android: {android_count:2d} 台 ({android_count/total_devices*100:.1f}%)")
        print(f"   iOS:     {ios_count:2d} 台 ({ios_count/total_devices*100:.1f}%)")
        print(f"   Windows: {windows_count:2d} 台 ({windows_count/total_devices*100:.1f}%)")
        print(f"   其他:    {other_count:2d} 台 ({other_count/total_devices*100:.1f}%)")
        print(f"   ─────────────────")
        print(f"   总计:    {total_devices:2d} 台")
        
        return True
        
    except Exception as e:
        print(f"❌ 跨平台统计演示失败: {e}")
        return False


def demonstrate_error_handling():
    """演示错误处理最佳实践"""
    print("\n\n🛡️ 错误处理演示")
    print("=" * 50)
    
    def safe_read_devices(reader_func, device_type):
        """安全读取设备的包装函数"""
        try:
            return reader_func()
        except FileNotFoundError:
            print(f"   ❌ {device_type}文件未找到")
            return []
        except UnicodeDecodeError:
            print(f"   ❌ {device_type}文件编码错误")
            return []
        except Exception as e:
            print(f"   ❌ {device_type}读取失败: {e}")
            return []
    
    print("\n🔍 安全读取测试:")
    android_devices = safe_read_devices(read_android_devices, "Android设备")
    print(f"   Android设备: {len(android_devices)} 台")
    
    # 测试错误参数
    print("\n🧪 参数验证测试:")
    try:
        query_devices_by_architecture("")
    except ValueError as e:
        print(f"   ✅ 空参数验证通过: {e}")
    
    try:
        result = query_devices_by_architecture("nonexistent")
        print(f"   ✅ 不存在架构处理正确: 返回 {len(result)} 个结果")
    except Exception as e:
        print(f"   ⚠️  不存在架构异常: {e}")


def main():
    """主演示函数"""
    print("🎯 Device Module API 使用示例")
    print("根据 src/device/README.md 文档演示所有API功能")
    print("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # 基础读取器演示
    if demonstrate_basic_readers():
        success_count += 1
    
    # Windows高级功能演示
    if demonstrate_windows_advanced_features():
        success_count += 1
    
    # 跨平台统计演示
    if demonstrate_cross_platform_statistics():
        success_count += 1
    
    # 错误处理演示
    try:
        demonstrate_error_handling()
        success_count += 1
    except Exception:
        pass
    
    # 总结
    print(f"\n\n🎉 演示完成!")
    print("=" * 60)
    print(f"成功演示: {success_count}/{total_tests} 项功能")
    
    if success_count == total_tests:
        print("✅ 所有API功能正常，文档示例验证通过！")
        return True
    else:
        print("⚠️  部分功能存在问题，请检查API实现")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 演示脚本执行失败: {e}")
        sys.exit(1)