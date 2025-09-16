#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记录CSV文件读取器
"""

import csv
import os
from pathlib import Path


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


if __name__ == "__main__":
    try:
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
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        exit(1)