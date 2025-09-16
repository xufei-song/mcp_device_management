# Device Module API Documentation

## 概述

`src/device` 模块提供了完整的设备数据读取和查询功能，支持多种设备类型的CSV文件读取，并为Windows设备提供了高级查询能力。

## 📁 模块结构

```
src/device/
├── android_reader.py      # Android设备读取器
├── ios_reader.py          # iOS设备读取器
├── windows_reader.py      # Windows设备读取器（增强功能）
├── other_reader.py        # 其他设备读取器
├── records_reader.py      # 记录读取器
├── test_all_readers.py    # 统一测试脚本
└── __init__.py
```

## 🔧 核心API接口

### 1. Android设备读取器 (`android_reader.py`)

#### `read_android_devices()`
读取Android设备CSV文件并返回所有设备信息。

**返回值：**
- `list`: 包含所有Android设备信息的列表

**异常：**
- `FileNotFoundError`: CSV文件不存在
- `UnicodeDecodeError`: 文件编码错误
- `Exception`: 其他读取错误

**使用示例：**
```python
from src.device.android_reader import read_android_devices

try:
    devices = read_android_devices()
    print(f"读取到 {len(devices)} 台Android设备")
    for device in devices:
        print(f"设备: {device['设备名称']}, 状态: {device['设备状态']}")
except Exception as e:
    print(f"读取失败: {e}")
```

**数据字段：**
- 创建日期、设备名称、设备OS、SKU、类型、品牌
- 借用者、所属manager、设备序列号、资产编号
- 是否盘点、设备状态、列1

---

### 2. iOS设备读取器 (`ios_reader.py`)

#### `read_ios_devices()`
读取iOS设备CSV文件并返回所有设备信息。

**返回值：**
- `list`: 包含所有iOS设备信息的列表

**异常：**
- `FileNotFoundError`: CSV文件不存在
- `UnicodeDecodeError`: 文件编码错误
- `Exception`: 其他读取错误

**使用示例：**
```python
from src.device.ios_reader import read_ios_devices

devices = read_ios_devices()
# 筛选可用设备
available_devices = [d for d in devices if d['设备状态'] == '可用']
```

**数据字段：**
- 创建日期、设备名称、设备OS、设备序列号
- 借用者、所属manager、资产编号、是否盘点、设备状态、列1

---

### 3. Windows设备读取器 (`windows_reader.py`) ⭐ **增强功能**

#### `read_windows_devices()`
读取Windows设备CSV文件并返回所有设备信息。

**返回值：**
- `list`: 包含所有Windows设备信息的列表

**数据字段：**
- 创建日期、设备OS、设备名称、SKU、芯片架构
- 借用者、所属manager、设备序列号、资产编号
- 是否盘点、设备状态、列1

#### `get_all_architectures()` 🆕
获取所有芯片架构列表。

**返回值：**
- `list`: 包含所有不同芯片架构的列表（去重并排序）

**使用示例：**
```python
from src.device.windows_reader import get_all_architectures

architectures = get_all_architectures()
print(f"支持的架构: {architectures}")
# 输出: ['arm64', 'x64']
```

#### `query_devices_by_architecture(architecture)` 🆕
根据芯片架构查询设备。

**参数：**
- `architecture` (str): 要查询的芯片架构字符串

**返回值：**
- `list`: 匹配指定芯片架构的设备列表

**异常：**
- `ValueError`: 架构参数为空
- `Exception`: 读取文件或处理数据错误

**使用示例：**
```python
from src.device.windows_reader import query_devices_by_architecture

# 查询x64架构的设备
x64_devices = query_devices_by_architecture('x64')
available_x64 = [d for d in x64_devices if d['设备状态'] == '可用']

# 查询arm64架构的设备
arm64_devices = query_devices_by_architecture('arm64')
```

---

### 4. 其他设备读取器 (`other_reader.py`)

#### `read_other_devices()`
读取其他设备CSV文件并返回所有设备信息。

**返回值：**
- `list`: 包含所有其他设备信息的列表

**数据字段：**
- 创建日期、设备名称、SKU、设备OS、设备序列号
- 借用者、所属manager、资产编号、是否盘点、设备状态、列1

---

### 5. 记录读取器 (`records_reader.py`)

#### `read_records()`
读取记录CSV文件并返回所有借用/归还记录。

**返回值：**
- `list`: 包含所有记录信息的列表

**数据字段：**
- 创建日期、借用者、设备、资产编号、状态、原因

**使用示例：**
```python
from src.device.records_reader import read_records

records = read_records()
# 查看最近的借用记录
recent_borrows = [r for r in records if r['状态'] == '借用']
```

---

## 🚀 命令行接口

### Windows设备查询命令
```bash
# 显示所有Windows设备
python src/device/windows_reader.py

# 显示所有芯片架构
python src/device/windows_reader.py arch

# 查询x64架构设备
python src/device/windows_reader.py query x64

# 查询arm64架构设备  
python src/device/windows_reader.py query arm64
```

### 其他设备读取命令
```bash
# 读取各类设备
python src/device/android_reader.py
python src/device/ios_reader.py
python src/device/other_reader.py
python src/device/records_reader.py

# 运行所有读取器测试
python src/device/test_all_readers.py
```

---

## 📊 数据统计

| 设备类型 | CSV文件 | 记录数量 | 特殊功能 |
|---------|---------|----------|----------|
| Android | `android_devices.csv` | 97条 | 基础读取 |
| iOS | `ios_devices.csv` | 60条 | 基础读取 |
| Windows | `windows_devices.csv` | 31条 | **架构查询** |
| 其他设备 | `other_devices.csv` | 11条 | 基础读取 |
| 记录 | `records.csv` | 17条 | 借用记录 |

## 🔍 高级查询示例

### 设备可用性查询
```python
from src.device.android_reader import read_android_devices

# 查询可用的Android手机
android_devices = read_android_devices()
available_phones = [
    device for device in android_devices 
    if device['设备状态'] == '可用' and device['类型'] == '手机'
]

print(f"可用Android手机: {len(available_phones)} 台")
```

### 跨平台设备统计
```python
from src.device.android_reader import read_android_devices
from src.device.ios_reader import read_ios_devices
from src.device.windows_reader import read_windows_devices

android_count = len(read_android_devices())
ios_count = len(read_ios_devices())
windows_count = len(read_windows_devices())

print(f"设备统计: Android({android_count}) + iOS({ios_count}) + Windows({windows_count}) = {android_count + ios_count + windows_count} 台")
```

### Windows架构分析
```python
from src.device.windows_reader import get_all_architectures, query_devices_by_architecture

# 获取架构统计
architectures = get_all_architectures()
for arch in architectures:
    devices = query_devices_by_architecture(arch)
    available = sum(1 for d in devices if d['设备状态'] == '可用')
    in_use = sum(1 for d in devices if d['设备状态'] == '正在使用')
    print(f"{arch}: 总计{len(devices)}台, 可用{available}台, 使用中{in_use}台")
```

---

## 🛠️ 集成指南

### 1. 模块导入
```python
# 导入单个读取器
from src.device.android_reader import read_android_devices
from src.device.windows_reader import read_windows_devices, get_all_architectures, query_devices_by_architecture

# 导入多个读取器
from src.device import android_reader, ios_reader, windows_reader
```

### 2. 错误处理最佳实践
```python
def safe_read_devices(reader_func):
    """安全读取设备的包装函数"""
    try:
        return reader_func()
    except FileNotFoundError:
        print("设备文件未找到，请检查Devices目录")
        return []
    except UnicodeDecodeError:
        print("文件编码错误，请确保使用UTF-8编码")
        return []
    except Exception as e:
        print(f"读取设备失败: {e}")
        return []

# 使用示例
android_devices = safe_read_devices(read_android_devices)
```

### 3. 数据验证
```python
def validate_device_data(devices):
    """验证设备数据完整性"""
    valid_devices = []
    for device in devices:
        # 检查必要字段
        if device.get('设备名称') and device.get('设备状态'):
            valid_devices.append(device)
        else:
            print(f"警告: 设备数据不完整 - {device}")
    return valid_devices
```

---

## 📝 注意事项

1. **文件编码**: 所有CSV文件必须使用UTF-8编码保存
2. **路径依赖**: 读取器使用相对路径，需要从项目根目录运行
3. **数据一致性**: 设备状态字段应保持一致（"可用"、"正在使用"、"设备异常"）
4. **异常处理**: 建议在集成时添加适当的异常处理
5. **性能考虑**: 对于频繁查询，考虑缓存CSV数据

---

## 🔮 未来扩展

- [ ] 添加设备数据缓存机制
- [ ] 支持设备数据修改接口
- [ ] 添加更多设备筛选条件
- [ ] 支持Excel文件格式
- [ ] 添加设备借用/归还接口
- [ ] 支持设备数据导出功能

---

**最后更新**: 2025年9月16日  
**版本**: v1.1 (新增Windows芯片架构查询功能)