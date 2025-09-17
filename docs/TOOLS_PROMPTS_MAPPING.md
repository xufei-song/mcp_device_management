# MCP设备管理系统 - 工具、提示和接口对应关系表

## 📋 完整对应关系表

| 序号 | MCP工具名称 | 对应提示 | 实际调用的接口/函数 | 功能描述 |
|------|------------|----------|-------------------|----------|
| 1 | `get_device_info` | `device_info_query` | `read_android_devices()`, `read_ios_devices()`, `read_windows_devices()` | 根据设备ID和类型获取设备详细信息 |
| 2 | `list_devices` | `device_list_guide` | `read_android_devices()`, `read_ios_devices()`, `read_windows_devices()`, `read_other_devices()` | 列出所有可用设备，支持类型和状态筛选 |
| 3 | `find_device_by_asset` | `asset_lookup_guide` | `find_device_by_asset_number()` | 根据资产编号在所有设备表中查找设备 |
| 4 | `borrow_device` | `device_borrow_workflow` | `borrow_device()` | 完整的设备借用流程（记录+状态更新） |
| 5 | `return_device` | `device_return_workflow` | `return_device()` | 完整的设备归还流程（记录+状态更新） |
| 6 | `get_windows_architectures` | `windows_architecture_guide` | `get_all_architectures()` | 获取所有Windows设备的芯片架构列表 |
| 7 | `query_devices_by_architecture` | `windows_architecture_guide` | `query_devices_by_architecture()` | 根据芯片架构查询Windows设备 |
| 8 | `get_device_records` | `device_records_analysis` | `read_records()` | 获取设备借用/归还记录 |

## 🔧 工具分类

### 设备信息查询工具
- **get_device_info**: 查询单个设备详细信息
- **list_devices**: 查询设备列表
- **find_device_by_asset**: 通过资产编号查找设备

### 设备借用归还工具
- **borrow_device**: 完整借用流程
- **return_device**: 完整归还流程

### Windows特定工具
- **get_windows_architectures**: 获取架构列表
- **query_devices_by_architecture**: 按架构查询设备

### 记录和系统工具
- **get_device_records**: 查询记录

## 📝 提示分类

### 查询指导类
1. **device_info_query**: 设备信息查询指导
2. **device_list_guide**: 设备列表查询和筛选指导
3. **asset_lookup_guide**: 资产编号查询指导

### 流程指导类
4. **device_borrow_workflow**: 设备借用流程指导
5. **device_return_workflow**: 设备归还流程指导

### 专项功能类
6. **windows_architecture_guide**: Windows设备架构查询指导
7. **device_records_analysis**: 设备记录分析模板

## 🔍 接口文件分布

### src/device/android_reader.py
- `read_android_devices()`: 读取Android设备CSV文件

### src/device/ios_reader.py
- `read_ios_devices()`: 读取iOS设备CSV文件

### src/device/windows_reader.py
- `read_windows_devices()`: 读取Windows设备CSV文件
- `get_all_architectures()`: 获取所有Windows架构
- `query_devices_by_architecture()`: 按架构查询设备

### src/device/other_reader.py
- `read_other_devices()`: 读取其他设备CSV文件

### src/device/records_reader.py
- `read_records()`: 读取借用/归还记录
- `find_device_by_asset_number()`: 根据资产编号查找设备
- `borrow_device()`: 完整借用流程
- `return_device()`: 完整归还流程

## 📊 覆盖情况统计

### 工具覆盖
- **总工具数**: 8个
- **有对应提示的工具**: 8个
- **提示覆盖率**: 100% (8/8)

### 提示覆盖
- **总提示数**: 5个
- **覆盖工具数**: 8个 (部分提示对应多个工具)
- **功能完整性**: 100% (所有主要业务功能都有提示指导)

### 接口调用
- **Android设备**: `read_android_devices()`
- **iOS设备**: `read_ios_devices()`
- **Windows设备**: `read_windows_devices()`, `get_all_architectures()`, `query_devices_by_architecture()`
- **其他设备**: `read_other_devices()`
- **记录管理**: `read_records()`, `find_device_by_asset_number()`, `borrow_device()`, `return_device()`

## 🎯 工具使用场景

### 日常查询场景
1. **查看设备信息**: `get_device_info` → `device_info_query`
2. **浏览设备列表**: `list_devices` → `device_list_guide`
3. **查找特定设备**: `find_device_by_asset` → `asset_lookup_guide`

### 设备管理场景
4. **借用设备**: `borrow_device` → `device_borrow_workflow`
5. **归还设备**: `return_device` → `device_return_workflow`

### 专项查询场景
6. **Windows架构查询**: `get_windows_architectures`/`query_devices_by_architecture` → `windows_architecture_guide`
7. **记录分析**: `get_device_records` → `device_records_analysis`

## 💡 使用建议

1. **新用户**: 建议先使用对应的提示获取操作指导
2. **熟练用户**: 可以直接调用工具进行操作
3. **开发集成**: 参考提示中的示例代码和最佳实践
4. **故障排除**: 提示中包含常见问题的解决方案

---

**最后更新**: 2025年1月17日  
**版本**: v2.0 (删除非必要工具和功能)  
**工具数量**: 8个  
**提示数量**: 5个  
**接口函数**: 10个